from flask import Flask, send_file, send_from_directory, make_response, request, abort, session, redirect, jsonify
import re, threading, datetime, time, os, random, string, base64
from flask_pymongo import PyMongo
# 此程序只能在64位机器上运行，否则可能溢出

password = "password"  # when deploy, change this !!!
imagepath = "/home/hwlab/"

def init(app, mongo, prefix):
    # 静态文件
    @app.route(prefix + '/', methods=['GET'])
    def hwlab_index():
        if "logined" in session:
            return app.send_static_file("hwlab/index.html")
        return redirect(prefix + "/login.html")
    @app.route(prefix + "/login.html", methods=['GET'])
    def hwlab_getpublic_login():
        return app.send_static_file("hwlab/login.html")
    @app.route(prefix + "/css/bootstrap.min.css", methods=['GET'])
    def hwlab_getpublic_bootstrap():
        return app.send_static_file("hwlab/css/bootstrap.min.css")
    @app.route(prefix + "/<path:path_name>", methods=['GET'])
    def hwlab_getstatic(path_name):
        if "logined" not in session:
            abort(404)
        return app.send_static_file("hwlab/" + path_name)

    # API
    @app.route(prefix + '/login', methods=['POST'])
    def hwlab_login():
        if "password" not in request.form:
            return "no password"
        if request.form["password"] != password:
            return "password error"
        session["logined"] = ''.join(random.sample(string.ascii_letters + string.digits, 32))
        return redirect(prefix)
    @app.route(prefix + "/query_all", methods=['GET'])
    def hwlab_query_all():
        if "logined" not in session: return redirect(prefix + "/login.html")
        hwlab = mongo.db.hwlab
        cursor = hwlab.find({})
        data = []
        for ele in cursor:
            del ele['_id']  # remove _id
            data.append(ele)
            print(ele)
        return jsonify({
            "data": data
        })
    nonminus = re.compile(r'^[0-9]+$')
    @app.route(prefix + "/add", methods=['POST'])
    def hwlab_add():
        if "logined" not in session: return redirect(prefix + "/login.html")
        hwlab = mongo.db.hwlab
        ele = {}
        if "name" not in request.form: return "no name"
        else: ele["name"] = request.form["name"]
        if hwlab.find_one({"name": ele["name"]}) is not None: return "duplicate name"
        if "quantity" not in request.form: return "no quantity"
        else: ele["quantity"] = request.form["quantity"]
        if not re.match(nonminus, ele["quantity"]): return "quantity invalid"
        ele["quantity"] = int(ele["quantity"])
        if "position" not in request.form: return "no position"
        else: ele["position"] = request.form["position"]
        if "description" not in request.form: return "no description"
        else: ele["description"] = request.form["description"]
        if "image" not in request.form: return "no image"
        else: ele["image"] = request.form["image"]
        if "lastmodified" not in request.form: return "no lastmodified"
        else: ele["lastmodified"] = request.form["lastmodified"]
        if not re.match(nonminus, ele["lastmodified"]): return "lastmodified invalid"
        ele["lastmodified"] = int(ele["lastmodified"])  # 可能溢出，需要在64位机器上运行
        i = 0
        tags = []
        while ("tag%d" % i) in request.form:
            tags.append(request.form["tag%d" % i])
            i += 1
        ele["tag"] = tags
        print(ele)
        hwlab.insert(ele) 
        return "OK"
    @app.route(prefix + "/modify", methods=['POST'])
    def hwlab_modify():
        if "logined" not in session: return redirect(prefix + "/login.html")
        hwlab = mongo.db.hwlab
        ele = {}
        if "name" not in request.form: return "no name"
        else: ele["name"] = request.form["name"]
        if "quantity" not in request.form: return "no quantity"
        else: ele["quantity"] = request.form["quantity"]
        if not re.match(nonminus, ele["quantity"]): return "quantity invalid"
        ele["quantity"] = int(ele["quantity"])
        if "position" not in request.form: return "no position"
        else: ele["position"] = request.form["position"]
        if "description" not in request.form: return "no description"
        else: ele["description"] = request.form["description"]
        if "image" not in request.form: return "no image"
        else: ele["image"] = request.form["image"]
        if "lastmodified" not in request.form: return "no lastmodified"
        else: ele["lastmodified"] = request.form["lastmodified"]
        if not re.match(nonminus, ele["lastmodified"]): return "lastmodified invalid"
        ele["lastmodified"] = int(ele["lastmodified"])  # 可能溢出，需要在64位机器上运行
        i = 0
        tags = []
        while ("tag%d" % i) in request.form:
            tags.append(request.form["tag%d" % i])
            i += 1
        ele["tag"] = tags
        print(ele)
        hwlab.update({"name": ele["name"]},{"$set": ele})
        return "OK"
    @app.route(prefix + "/uploadpic", methods=['POST'])
    def hwlab_uploadpic():
        if "base64" not in request.form or "type" not in request.form:
            return "error"
        base = request.form["base64"]
        print("base:", base[:40], "...", base[-20:])
        sp = base.split(',')
        data = base64.b64decode(sp[1])
        filename = ''.join(random.sample(string.ascii_letters + string.digits, 8)) + "." + sp[0].split("/")[1].split(";")[0]
        print(filename)
        if os.path.exists(imagepath + filename): return "error"
        with open(imagepath + filename, "wb") as f:
            f.write(data)
        return filename
    @app.route(prefix + "/getpic/<filename>", methods=['GET'])
    def hwlab_getpic(filename):
        global imagepath
        return send_from_directory(imagepath, filename)

if __name__ == "__main__":
    imagepath = os.path.dirname(__file__) + "/image_test/"
    print(imagepath)
    app = Flask(__name__, static_folder='')
    app.config['SECRET_KEY'] = '12345678'  # use os.urandom(24) to generate one when deploy
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/flask'
    mongo = PyMongo(app)
    init(app, mongo, "/hwlab")
    app.run(host='0.0.0.0', port=80, debug=True)
