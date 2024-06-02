import os
import random
import shutil
import fitz
import appbuilder
import streamlit as st


# 创建一个文件夹用于保存上传的文件
if not os.path.exists("upload_path"):
    os.makedirs("upload_path")

if "INPUT_TOPIC" not in st.session_state:
    st.session_state["INPUT_TOPIC"] = ""

# 设置环境变量
os.environ["APPBUILDER_TOKEN"] = "bce-v3/ALTAK-VlKbIY5HV9PlcHYw4DZVk/9006ccb56f1756c923064da093c78752fa7c0920"
app_id = "10bfb79d-a65e-4b16-b306-48cc2353514e"

# 初始化智能体
client = appbuilder.AppBuilderClient(app_id)
# 创建第一次默认会话
conversation_id = client.create_conversation()

# 页面标题和说明文字
st.set_page_config(page_title="答辩助手")
st.title("👩🏻‍🏫 论文模拟答辩助手")
st.write("👉🏼 请输入你论文主题，并上传PDF类型的论文文件！")

# 选择文件并重命名
thesis_topic = st.text_input("论文主题", value=st.session_state["INPUT_TOPIC"], max_chars=None, key=None, type='default')

# 上传论文文件
uploaded_file = st.file_uploader("选择文件", type="pdf")

saved = st.button("确定")
if saved:
    # 保存当前主题到会话
    st.session_state["INPUT_TOPIC"] = thesis_topic
    # 保存文件
    if uploaded_file is not None:
        if thesis_topic.strip():
            file_path = os.path.join("upload_path", thesis_topic + ".pdf")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"已保存文件: {file_path}")

            # 将pdf文档转为 图片
            pdf_path = os.path.join("upload_path", thesis_topic + ".pdf")
            # 定义图片保存的路径
            save_path = r'image_path'
            # 如果保存路径不存在，则创建该路径
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            # 打开PDF文件
            doc = fitz.open(pdf_path)
            # 遍历PDF的每一页
            for page_number in range(len(doc)):
                # 获取页面对象
                page = doc.load_page(page_number)
                # 将PDF页面转换为图片（pix对象）
                pix = page.get_pixmap(dpi=300)  # 设置DPI为300
                # 定义图片的保存路径和文件名
                image_path = os.path.join(save_path, f'page_{page_number + 1}.png')
                # 保存图片
                pix.save(image_path)
            # 关闭文档对象
            doc.close()


class Asking:
    def __init__(self, continued):
        self.continued = continued

    def asking_questions(self):
        # 获取源文件夹中所有文件名
        image_files = os.listdir("image_path")

        # 设置你想要随机获取的文件索引范围
        min_index = 3  # 可以根据需要调整
        max_index = len(image_files) - 3  # 可以根据需要调整
        # 在指定范围内随机选择一个索引
        random_index = random.randint(min_index, max_index)
        # 获取随机文件的完整路径
        random_file = os.path.join("image_path/", image_files[random_index])

        # # 随机获取其中一个文件
        # random_file = random.sample(image_files, 1)
        # # 上传随机选择的文件
        # local_file_path = "image_path/" + random_file[0]

        print("随机选择的页数-2：" + random_file)
        file_id = client.upload_local_file(conversation_id, random_file)
        # 引用上传的文档，开始对话
        message = client.run(conversation_id, "依据上传的论文文件生成1个问题？", file_ids=[file_id, ], stream=False)
        st.write("🤔问题: " + message.content.answer)

        prompt = st.text_input("请回答：", value="", max_chars=None, key=None, type='default')
        query = "请针对问题" + message.content.answer + ",以及我的回答" + prompt + "进行评价!"
        message = client.run(conversation_id, query,)
        st.write("🧑‍🏫很棒: " + message.content.answer)


# 下面展示聊天页面逻辑
chat = None
if st.session_state["INPUT_TOPIC"] != "":
    chat = st.session_state["INPUT_TOPIC"]

if chat:
    with st.container():
        st.header("👩🏻‍🏫开始对话吧")
        # 获取源文件夹中所有文件名
        image_files = os.listdir("image_path")
        # 设置你想要随机获取的文件索引范围
        min_index = 3  # 可以根据需要调整
        max_index = len(image_files) - 3  # 可以根据需要调整
        # 在指定范围内随机选择一个索引
        random_index = random.randint(min_index, max_index)
        # 获取随机文件的完整路径
        random_file = os.path.join("image_path/", image_files[random_index])

        # # 随机获取其中一个文件
        # random_file = random.sample(image_files, 1)
        # # 上传随机选择的文件
        # local_file_path = "image_path/" + random_file[0]

        print("随机选择的页数：" + random_file)
        file_id = client.upload_local_file(conversation_id, random_file)
        # 引用上传的文档，开始对话
        message = client.run(conversation_id, "依据上传的论文文件生成1个问题？", file_ids=[file_id, ], stream=False)
        st.write("🤔 第一个问题: " + message.content.answer)

        prompt = st.text_input("回答：", value="", max_chars=None, key=None, type='default')
        query = "请针对问题" + message.content.answer + ",以及我的回答" + prompt + "进行评价!"

        sendd = st.button("发送")
        if sendd:
            message = client.run(conversation_id, query,)
            st.write("🧑‍🏫很棒: " + message.content.answer)

        continued = st.button("💪 继续提问...")
        if continued:
            asking = Asking(continued)
            asking.asking_questions()


        closed = st.button("🫣 结束对话...")
        if closed:
            # 清除输入
            st.session_state["INPUT_TOPIC"] = ""

            # 清空文件夹文件，在创建新的文件夹
            shutil.rmtree('upload_path')
            os.mkdir('upload_path')
            shutil.rmtree('image_path')
            os.mkdir('image_path')
            uploaded_file = None
            thesis_topic = None
            st.rerun()

else:
    with st.container():
        st.warning("👮🏻‍ 请输入论文主题, 并上传文件...")
