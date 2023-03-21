from __future__ import print_function

import json
import os
import os.path as osp
import re
import shutil
import sys
import tempfile
import textwrap
import time

import requests
import six
import tqdm
from customtkinter import CTkSlider
from parse_url import parse_url

CHUNK_SIZE = 512 * 1024  # 512KB
home = osp.expanduser("~")


# textwrap.indent for Python2
def indent(text, prefix):
	def prefixed_lines():
		for line in text.splitlines(True):
			yield (prefix + line if line.strip() else line)

	return "".join(prefixed_lines())


def get_url_from_gdrive_confirmation(contents):
	url = ""
	for line in contents.splitlines():
		m = re.search(r'href="(\/uc\?export=download[^"]+)', line)
		if m:
			url = "https://docs.google.com" + m.groups()[0]
			url = url.replace("&amp;", "&")
			break
		m = re.search('id="download-form" action="(.+?)"', line)
		if m:
			url = m.groups()[0]
			url = url.replace("&amp;", "&")
			break
		m = re.search('"downloadUrl":"([^"]+)', line)
		if m:
			url = m.groups()[0]
			url = url.replace("\\u003d", "=")
			url = url.replace("\\u0026", "&")
			break
		m = re.search('<p class="uc-error-subcaption">(.*)</p>', line)
		if m:
			error = m.groups()[0]
			raise RuntimeError(error)
	if not url:
		raise RuntimeError(
			"Cannot retrieve the public link of the file. "
			"You may need to change the permission to "
			"'Anyone with the link', or have had many accesses."
		)
	return url


def _get_session(proxy, use_cookies, return_cookies_file=False):
	sess = requests.session()

	sess.headers.update(
		{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)"}
	)

	if proxy is not None:
		sess.proxies = {"http": proxy, "https": proxy}
		print("Using proxy:", proxy, file=sys.stderr)

	# Load cookies if exists
	cookies_file = osp.join(home, ".cache/gdown/cookies.json")
	if osp.exists(cookies_file) and use_cookies:
		with open(cookies_file) as f:
			cookies = json.load(f)
		for k, v in cookies:
			sess.cookies[k] = v

	if return_cookies_file:
		return sess, cookies_file
	else:
		return sess


def download(
	url=None,
	output=None,
	quiet=False,
	proxy=None,
	speed=None,
	use_cookies=True,
	verify=True,
	id=None,
	fuzzy=False,
	resume=False,
):
	global pb, output_file_name

	if not (id is None) ^ (url is None):
		raise ValueError("Either url or id has to be specified")
	if id is not None:
		url = "https://drive.google.com/uc?id={id}".format(id=id)

	url_origin = url

	sess, cookies_file = _get_session(
		proxy=proxy, use_cookies=use_cookies, return_cookies_file=True
	)

	gdrive_file_id, is_gdrive_download_link = parse_url(url, warning=not fuzzy)

	if fuzzy and gdrive_file_id:
		# overwrite the url with fuzzy match of a file id
		url = "https://drive.google.com/uc?id={id}".format(id=gdrive_file_id)
		url_origin = url
		is_gdrive_download_link = True

	while True:
		try:
			res = sess.get(url, stream=True, verify=verify)
		except requests.exceptions.ProxyError as e:
			print(
				"An error has occurred using proxy:",
				sess.proxies,
				file=sys.stderr,
			)
			print(e, file=sys.stderr)
			return

		if use_cookies:
			if not osp.exists(osp.dirname(cookies_file)):
				os.makedirs(osp.dirname(cookies_file))
			# Save cookies
			with open(cookies_file, "w") as f:
				cookies = [
					(k, v)
					for k, v in sess.cookies.items()
					if not k.startswith("download_warning_")
				]
				json.dump(cookies, f, indent=2)

		if "Content-Disposition" in res.headers:
			# This is the file
			break
		if not (gdrive_file_id and is_gdrive_download_link):
			break

		# Need to redirect with confirmation
		try:
			url = get_url_from_gdrive_confirmation(res.text)
		except RuntimeError as e:
			print("Access denied with the following error:")
			error = "\n".join(textwrap.wrap(str(e)))
			error = indent(error, "\t")
			print("\n", error, "\n", file=sys.stderr)
			print(
				"You may still be able to access the file from the browser:",
				file=sys.stderr,
			)
			print("\n\t", url_origin, "\n", file=sys.stderr)
			return

	if gdrive_file_id and is_gdrive_download_link:
		content_disposition = six.moves.urllib_parse.unquote(
			res.headers["Content-Disposition"]
		)
		m = re.search(r"filename\*=UTF-8''(.*)", content_disposition)
		filename_from_url = m.groups()[0]
		filename_from_url = filename_from_url.replace(osp.sep, "_")
	else:
		filename_from_url = osp.basename(url)

	if output is None:
		output = filename_from_url

	output_is_path = isinstance(output, six.string_types)
	if output_is_path and output.endswith(osp.sep):
		if not osp.exists(output):
			os.makedirs(output)
		output = osp.join(output, filename_from_url)

	if output_is_path:
		existing_tmp_files = []
		for file in os.listdir(osp.dirname(output) or "."):
			if file.startswith(osp.basename(output)):
				existing_tmp_files.append(osp.join(osp.dirname(output), file))
		if resume and existing_tmp_files:
			if len(existing_tmp_files) != 1:
				print(
					"There are multiple temporary files to resume:",
					file=sys.stderr,
				)
				print("\n")
				for file in existing_tmp_files:
					print("\t", file, file=sys.stderr)
				print("\n")
				print(
					"Please remove them except one to resume downloading.",
					file=sys.stderr,
				)
				return
			tmp_file = existing_tmp_files[0]
		else:
			resume = False
			# mkstemp is preferred, but does not work on Windows
			# https://github.com/wkentaro/gdown/issues/153
			tmp_file = tempfile.mktemp(
				suffix=tempfile.template,
				prefix=osp.basename(output),
				dir=osp.dirname(output),
			)
		f = open(tmp_file, "ab")
	else:
		tmp_file = None
		f = output

	if tmp_file is not None and f.tell() != 0:
		headers = {"Range": "bytes={}-".format(f.tell())}
		res = sess.get(url, headers=headers, stream=True, verify=verify)

	if not quiet:
		print("Downloading...", file=sys.stderr)
		if resume:
			print("Resume:", tmp_file, file=sys.stderr)
		print("From:", url_origin, file=sys.stderr)
		print(
			"To:",
			osp.abspath(output) if output_is_path else output,
			file=sys.stderr,
		)

	try:
		total = res.headers.get("Content-Length")
		if total is not None:
			total = int(total)
		if not quiet:
			pbar = tqdm.tqdm(total=total, unit="B", unit_scale=True)
		t_start = time.time()
		for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
			f.write(chunk)
			if not quiet:
				pbar.update(len(chunk))
				pb['value'] += ((len(chunk)/total)*50)
				pb.update()
				str_display  = "Updating " + output_file_name +" " + str(int(pb['value']))+"%"
				lb_status.config(text=str_display)
				lb_status.update()
				#print (pb['value'])
			if speed is not None:
				elapsed_time_expected = 1.0 * pbar.n / speed
				elapsed_time = time.time() - t_start
				if elapsed_time < elapsed_time_expected:
					time.sleep(elapsed_time_expected - elapsed_time)
		if not quiet:
			pbar.close()
		if tmp_file:
			f.close()
			shutil.move(tmp_file, output)
	except IOError as e:
		print(e, file=sys.stderr)
		return
	finally:
		sess.close()

	return output

output_file_name = ""

def update():
	root.config(cursor="watch")
	start_button.config(text="Updating")
	start_button.config(state=DISABLED)
	global pb,lb_status
	output_file_name = 'Generate_Mean_Face_NewUI.exe'
	lb_status.config(text="Update "+output_file_name)
	lb_status.update()
	
	url = 'https://drive.google.com/file/d/1yT5RpH0-ck-hIg4iTpCtQuxsnopIrHB3/view?usp=share_link'
	download(url, output_file_name, quiet=False,fuzzy=True)
	print ("Done")

	#pb['value'] = 0
	
	lb_status.update()
	output_file_name = 'Mask_Out_NewUI.exe'
	lb_status.config(text="Update "+output_file_name)
	lb_status.update()
	url = 'https://drive.google.com/file/d/1S0xTIQZuyuJGYMAo6xBXU66Ay_Gpat1r/view?usp=sharing'
	download(url, output_file_name, quiet=False,fuzzy=True)
	print ("Done")

	lb_status.config(text="Finished updating!")
	lb_status.update()
	start_button.config(state=NORMAL)
	start_button.config(text="Finish!")
	start_button.config(command=Close)
	start_button.update()
	root.config(cursor="")

def Close():
	root.destroy()
	root.quit()
	
from tkinter import *
from tkinter import ttk
from control import button_color, background_color, MyButton
if __name__ == '__main__':

	# root window
	root = Tk()
	#root.iconbitmap("icon_update.ico")
	root.geometry('300x110')
	root.title("Update GUI_Mask_Out chgiang@2023")
	root.config(background=background_color)
	root.grid()

	lb_status = Label(root, text="Update",background=background_color,fg='white',height=1,width=35,  justify=LEFT,anchor="w")
	lb_status.grid(row=0, column=0, pady=5, padx=0,columnspan=3)

	pb = ttk.Progressbar(
	root,
	orient='horizontal',
	mode='determinate',
	length=250
	)
	pb.grid(column=0, row=1, padx=20, pady=0)
	pb['value'] =0 

	start_button = MyButton(
	root,
	text='Update!',
	command=update
	)
	start_button.grid(column=0, row=2, padx=10, pady=15)


	root.mainloop()

	