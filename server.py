from connectonion import Agent, host

def create_agent():
    return Agent(
        "remote-assistant",
        system_prompt="You are a helpful remote agent.",
        model="co/gemini-2.5-flash",
    )

host(
    create_agent,
    port=8000,
    trust="open",       # 开发期：允许任何已签名客户端
    relay_url=None,     # 只走直连 ws，不走 ConnectOnion relay
)
