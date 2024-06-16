import os
import random
import fitz
import appbuilder
import streamlit as st


# 创建一个文件夹用于保存上传的文件
if not os.path.exists("upload_path"):
    os.makedirs("upload_path")

if "INPUT_TOPIC" not in st.session_state:
    st.session_state["INPUT_TOPIC"] = ""

if "INPUT_SPECIALIZED" not in st.session_state:
    st.session_state["INPUT_SPECIALIZED"] = ""

# 设置环境变量
os.environ["APPBUILDER_TOKEN"] = "bce-v3/ALTAK-VlKbIY5HV9PlcHYw4DZVk/9006ccb56f1756c923064da093c78752fa7c0920"
app_id = "10bfb79d-a65e-4b16-b306-48cc2353514e"

# 初始化智能体
client = appbuilder.AppBuilderClient(app_id)

# 页面标题和说明文字
st.set_page_config(page_title="答辩助手")
st.title("👩🏻‍🏫 论文模拟答辩助手")
st.write("👉🏼 请输入你的专业以及论文题目，并上传PDF类型的论文文件！")

# 选择文件并重命名
thesis_specialized = st.text_input("学习专业", value=st.session_state["INPUT_SPECIALIZED"], max_chars=None, key=None, type='default')

thesis_topic = st.text_input("论文题目", value=st.session_state["INPUT_TOPIC"], max_chars=None, key=None, type='default')

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

        print("随机选择的页数：" + random_file)

        # 创建一个对话ID
        conversation_id = client.create_conversation()
        file_id = client.upload_local_file(conversation_id, random_file)
        # 引用上传的文档，开始对话
        message = client.run(conversation_id, "根据图片中的内容以及数据库中模拟答辩的通用问题，生成对应的一个问题，要求优先出数据中通用问题，在出与图片中展示内容相关的问题。", file_ids=[file_id, ],)
        st.write("🤔 提问: " + message.content.answer)

        return message.content.answer
            

def send_dialogue(query):
    conversation_id = client.create_conversation()
    message = client.run(conversation_id, query,)
    return message.content.answer

# 下面展示聊天页面逻辑
chat = None
if st.session_state["INPUT_TOPIC"] != "":
    chat = st.session_state["INPUT_TOPIC"]

if chat:
    container = st.container()
    with container:
        st.header("👩🏻‍🏫 开始对话吧")
        st.write("👉🏼 只有三次提问机会，请珍惜使用机会，并确保提问与论文题目相关，避免出现题目无关的情况。")

        # 初始化 session_state
        if "count" not in st.session_state:
            st.session_state.count = 0

        if "result" not in st.session_state:
            st.session_state.result = ""

        if "input_key" not in st.session_state:
            st.session_state.input_key = ""

        continued = st.button("💪 生成问题")
        if continued:
            asking = Asking(continued)
            st.session_state.result = asking.asking_questions()

        if st.session_state.result:
            # 用户输入回答
            prompt = st.text_input("回答：", value=st.session_state.input_key, key="text_input_key")
            sended = st.button("发送")
            if sended:
                if prompt:
                    query = f"请针对以上提出的问题：{st.session_state.result} ,以及用户输入的回答：{prompt} ,进行点评，并且给出相应的建议，避免下次出现问题。如果回答与提出的问题无关联，则直接回复，跟 题目无关，并鼓励好好作答。如果回答与提出的问题有相关性，则给出相应的建议，鼓励好好作答。最终结果需要展示出问题，回答，建议，以及建议的回答。"
                    msg = send_dialogue(query)
                    st.write("🧑‍🏫 " + msg)
                    st.session_state.count += 1
                    # 清空输入框
                    st.session_state.input_key = ""
                    # st.experimental_rerun()
                else:
                    st.write("🧑‍🏫 请输入回答...")

        if st.session_state.count >= 3:
            st.write("****************************************************")
            st.write("👋🏻👋🏻👋🏻 对话结束，感谢使用。如需再次练习，请刷新页面，重新开始。")
else:
    with st.container():
        st.warning("👮🏻‍ 请输入论文题目, 并上传文件...")
