from flask import Flask, render_template, url_for, request, redirect
import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase Admin SDK
cred = credentials.Certificate("firebase_key.json")  # 替換為你的 Firebase 服務帳戶密鑰文件
firebase_admin.initialize_app(cred)

# 初始化 Firestore 客戶端
db = firestore.client()

app = Flask(__name__)

# 首頁：顯示所有公司名稱（集合名稱）
@app.route("/")
def index():
    collections = db.collections()  # 獲取所有集合
    company_names = [collection.id for collection in collections]  # 提取集合名稱
    return render_template("index.html", company_names=company_names)


# 公司詳情頁：顯示該集合內的文檔列表
@app.route("/company/<collection_name>")
def company_documents(collection_name):
    docs = db.collection(collection_name).stream()  # 獲取該集合的所有文檔
    documents = [{"id": doc.id, **doc.to_dict()} for doc in docs]  # 提取文檔 ID 和數據
    return render_template("company.html", collection_name=collection_name, documents=documents)

@app.route("/<collection_name>/<document_id>", methods=["GET", "POST"])
def document_details(collection_name, document_id):
    if request.method == "POST":
        # 獲取表單數據
        driver = request.form.get("driver")
        phone = request.form.get("phone")
        car_number = request.form.get("car_number")
        car_model = request.form.get("car_model")

        # 更新 Firestore 文檔
        db.collection(collection_name).document(document_id).update({
            "駕駛": driver,
            "電話": phone,
            "車號": car_number,
            "車型": car_model,
        })

        return redirect(url_for("company_documents", collection_name=collection_name))

    # GET 請求顯示當前文檔詳情
    doc = db.collection(collection_name).document(document_id).get()
    details = doc.to_dict()
    return render_template("document.html", collection_name=collection_name, document_id=document_id, details=details)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
