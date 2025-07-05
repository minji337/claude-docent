import streamlit as st
from course_client_obj import CourseClient
import asyncio
import threading
from anthropic import Anthropic


@st.cache_resource
def _get_loop():
    loop = asyncio.new_event_loop()
    th = threading.Thread(target=loop.run_forever, daemon=True)
    th.start()
    return loop


def run_async(coro):
    loop = _get_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()


@st.cache_resource
def get_course_resource():
    async def _connect():
        client = CourseClient()
        await client.connect_server()
        await client.setup_context()
        return client

    return run_async(_connect()), Anthropic()


course_client, anthropic_client = get_course_resource()


def call_llm(messages: list):
    response = anthropic_client.messages.create(
        max_tokens=1024,
        temperature=0.0,
        messages=messages,
        model="claude-3-5-haiku-20241022",
        tools=st.session_state.tools,
    )

    if response.stop_reason == "tool_use":
        tool_content = next(
            content for content in response.content if content.type == "tool_use"
        )
        tool_name = tool_content.name
        tool_input = tool_content.input
        tool_response = run_async(course_client.call_tool(tool_name, tool_input))
        messages.extend(
            [
                {"role": "assistant", "content": response.content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_content.id,
                            "content": str(tool_response),
                        }
                    ],
                },
            ]
        )
        return call_llm(messages)
    else:
        return response.content[0].text


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.tools = []


def handle_resource_select():
    if st.session_state.selected_resource_name == "선택 안함":
        st.session_state.selected_resource = None
    else:
        st.session_state.selected_resource = course_client.resource_map[
            st.session_state.selected_resource_name
        ]


def on_resource_confirm(rtext: str):
    st.session_state.context = st.session_state.resource_text_area
    st.session_state.selected_resource = None  # 뷰어 닫기
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": f"[context]사용자의 질문에 다음을 근거로 답할 것: {rtext}",
        }
    )


def handle_prompt_select():
    if st.session_state.selected_prompt_name == "선택 안함":
        st.session_state.selected_prompt = None
    else:
        st.session_state.selected_prompt = {
            "prompt_name": st.session_state.selected_prompt_name,
            "argument_names": course_client.prompt_map[
                st.session_state.selected_prompt_name
            ],
        }


def on_prompt_confirm(prompt_name, argument_names):
    arguments = {}
    for argument_name in argument_names:
        arguments[argument_name] = st.session_state.get(argument_name, "")

    prompt = run_async(course_client.get_prompt(prompt_name, arguments))

    st.session_state.context = prompt
    st.session_state.selected_prompt = None  # 뷰어 닫기

    st.session_state.chat_history.append(
        {"role": "user", "content": st.session_state.context}
    )

    resp = call_llm(st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "assistant", "content": resp})


def main():
    st.session_state.setdefault("context", "")
    st.session_state.setdefault("selected_resource_name", "선택 안함")
    st.session_state.setdefault("selected_resource", None)
    st.session_state.setdefault("selected_prompt_name", "선택 안함")
    st.session_state.setdefault("selected_prompt", None)
    st.session_state["tools"] = course_client.tools

    col1, col2 = st.columns(2)

    with col1:
        resource_names = list(course_client.resource_map.keys())
        st.selectbox(
            "리소스 선택",
            ["선택 안함"] + resource_names,
            key="selected_resource_name",
            on_change=handle_resource_select,
        )

        if st.session_state.selected_resource is not None:
            rtext = run_async(
                course_client.read_resource(st.session_state.selected_resource)
            )

            st.markdown(
                """
                <style>
                    textarea {
                        font-size: 12px !important;   
                        line-height: 1.4;             
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.text_area(
                "리소스",
                rtext,
                height=500,
                key="resource_text_area",
            )

            st.button("확인", on_click=on_resource_confirm, args=(rtext,))

    with col2:
        prompt_names = list(course_client.prompt_map.keys())
        st.selectbox(
            "프롬프트 템플릿 선택",
            ["선택 안함"] + prompt_names,
            key="selected_prompt_name",
            on_change=handle_prompt_select,
        )

        if st.session_state.selected_prompt is not None:
            prompt_name = st.session_state.selected_prompt["prompt_name"]
            argument_names = st.session_state.selected_prompt["argument_names"]
            for argument_name in argument_names:
                st.text_input(argument_name, key=argument_name)

            st.button(
                "확인",
                on_click=on_prompt_confirm,
                args=(prompt_name, argument_names),
            )

    user_message = st.chat_input("메시지를 입력하세요")
    if user_message:
        with st.chat_message("user"):
            st.markdown(user_message)
            st.session_state.chat_history.append(
                {"role": "user", "content": user_message}
            )
            resp = call_llm(st.session_state.chat_history)
        with st.chat_message("assistant"):
            st.session_state.chat_history.append({"role": "assistant", "content": resp})
            st.markdown(resp)
    else:
        for message in st.session_state.chat_history[-2:]:
            if "[context" in message["content"]:
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


if __name__ == "__main__":
    main()
