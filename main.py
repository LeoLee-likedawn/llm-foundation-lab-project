import sys
import gradio as gr
from start_service import call_my_service

def main():

    with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="slate",
        secondary_hue="blue",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Noto Sans")]
    )
    ) as demo:
        # CSS 삽입 (파스텔톤 하늘색 배경)
        gr.HTML(
            """
            <style>
                body {
                    background-color: #aee6f9; /* 파스텔톤 하늘색 배경 */
                }
                .big-chatbot {
                    height: 500px !important;
                    width: 100% !important;
                    font-size: 12px;
                }
                /* 사용자 메시지 */
                .big-chatbot [data-role="user"] .message {
                    background-color: #d7f3f7 !important;  /* 파스텔 하늘색 */
                    color: #000 !important;
                    font-size: 12px !important;
                    border-radius: 12px;
                    padding: 8px 12px;
                }
                /* 봇 메시지 */
                .big-chatbot [data-role="assistant"] .message {
                    background-color: #e6d7f7 !important;  /* 파스텔 보라색 */
                    color: #000 !important;
                    font-size: 12px !important;
                    border-radius: 12px;
                    padding: 8px 12px;
                }
            </style>
            """
        )

        gr.Markdown(
            """
            <div style='display:flex; align-items:center; justify-content:center; gap:10px;'>
                <img src="https://github.com/LeoLee-likedawn/llm-foundation-lab-project/raw/main/images/tuniverse.png" width="40" height="40" style="border-radius:50%;" />
                <h1 style='margin:0; font-size:24px;'>T우주 연동 Q&A 서비스</h1>
            </div>
            <p style='text-align:center; font-size:16px; color:gray;'>
            
            </p>
            """
        )

        #chatbot_ui = gr.Chatbot(elem_classes="big-chatbot")
        chatbot_ui = gr.Chatbot(
            elem_classes="big-chatbot",
            label="대화창",
            avatar_images=("https://raw.githubusercontent.com/LeoLee-likedawn/llm-foundation-lab-project/main/images/user.png", "https://raw.githubusercontent.com/LeoLee-likedawn/llm-foundation-lab-project/main/images/tbot.png"),  # 사용자/봇 아바타
            height=500,
        )
        
        msg = gr.Textbox(
            placeholder="문의사항을 입력하세요...",
            show_label=False,
            container=False,
        )
        clear = gr.Button("Clear")

        msg.submit(call_my_service, [msg, chatbot_ui], [chatbot_ui, chatbot_ui])
        msg.submit(lambda: "", None, msg)
        clear.click(lambda: None, None, chatbot_ui)

        demo.launch()


if __name__ == "__main__":
    main()
