import json


def pretty_print_chat_completion(response):
    """Print a readable step-by-step summary of a chat completion response:
    every tool call made along the way (with arguments and results), followed
    by the final assistant message."""

    steps = getattr(response.choices[0], "intermediate_messages", None)

    if steps:
        for step in steps:
            role = step.get("role") if isinstance(step, dict) else getattr(step, "role", None)

            if role == "tool":
                content = step["content"] if isinstance(step, dict) else step.content
                print(f"  ↳ result: {content}")
                continue

            tool_calls = step.get("tool_calls") if isinstance(step, dict) else getattr(step, "tool_calls", None)
            if tool_calls:
                print("🔧 Tool call(s):")
                for call in tool_calls:
                    fn = call["function"] if isinstance(call, dict) else call.function
                    name = fn["name"] if isinstance(fn, dict) else fn.name
                    args = fn["arguments"] if isinstance(fn, dict) else fn.arguments
                    try:
                        args = json.dumps(json.loads(args))
                    except (TypeError, json.JSONDecodeError):
                        pass
                    print(f"  - {name}({args})")
        print()

    print("💬 Final response:")
    print(response.choices[0].message.content)
