from flask import Flask, request, redirect, jsonify, render_template, url_for
import os
from werkzeug.utils import secure_filename
import main
import time

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "resumes"

def extract_file_name(pdfFile):
	# Extracts the file name
	return pdfFile.partition(".")[0][::-1].partition('/')[0][::-1]

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/resume/<fileName>")
def index2(fileName):
	return render_template("index2.html", fileName=fileName)

def pdf_to_png(filename):
	if '.pdf' in filename:
		os.system("convert -density 300 {} {}".format(filename, filename.replace(".pdf", ".png")))
		os.system("rm {}".format(filename))

@app.route("/sendfile", methods=["POST"])
def send_file():
	fileob = request.files["file2upload"]
	filename = secure_filename(fileob.filename)
	save_path = "{}/{}".format(app.config["UPLOAD_FOLDER"], filename)
	fileob.save(save_path)

	# open and close to update the access time.
	with open(save_path, "r") as f:
		pass
	pdf_to_png(save_path)
	main.convertAll(save_path)
	x = "mv resumes/{}* static/".format(extract_file_name(save_path))
	print x
	time.sleep(.5)
	os.system(x)
	time.sleep(.5)
	return "/resume/{}".format(extract_file_name(save_path))
	#return redirect(url_for('index2',fileName=extract_file_name(save_path)))
	#return "successful_upload"


@app.route("/filenames", methods=["GET"])
def get_filenames():
	filenames = os.listdir("resumes/")

	#modify_time_sort = lambda f: os.stat("uploads/{}".format(f)).st_atime

	def modify_time_sort(file_name):
		file_path = "resumes/{}".format(file_name)
		file_stats = os.stat(file_path)
		last_access_time = file_stats.st_atime
		return last_access_time

	filenames = sorted(filenames, key=modify_time_sort)
	return_dict = dict(filenames=filenames)
	return jsonify(return_dict)

if __name__ == '__main__':
	#raw_input(extract_file_name("/home/christopher/Github/TrueResume/resume.png"))
	app.run(debug=False)
