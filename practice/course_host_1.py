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



def main():
    st.session_state["tools"] = course_client.tools    
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


if __name__ == "__main__":
    main()
