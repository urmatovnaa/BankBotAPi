import logging
import httpx
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from gemini_function_schemas import gemini_function_schemas

AITIL_API_URL = "https://chat.aitil.kg/suroo"

def generate_function_docs():
    docs = []
    for fname, schema in gemini_function_schemas.items():
        params = schema.get("parameters", {}).get("properties", {})
        param_list = ", ".join(params.keys()) if params else "нет параметров"
        docs.append(f"{fname}: параметры — {param_list}")
    return "\n".join(docs)

def get_allowed_params(func_name):
    schema = gemini_function_schemas.get(func_name)
    if not schema:
        return set()
    return set(schema.get("parameters", {}).get("properties", {}).keys())

def cast_param_value(param_name, value, func_name):
    schema = gemini_function_schemas.get(func_name, {})
    param_schema = schema.get("parameters", {}).get("properties", {}).get(param_name, {})
    param_type = param_schema.get("type")
    if param_type == "number":
        try:
            return float(value)
        except Exception:
            return value
    if param_type == "integer":
        try:
            return int(value)
        except Exception:
            return value
    if param_type == "string":
        return str(value)
    return value

async def call_mcp_tool(tool_name, **kwargs):
    try:
        params = StdioServerParameters(
            command="python",
            args=["banking_mcp_server.py"],
            env={}
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=kwargs)
                return result.content[0].text if result.content else "Пустой ответ"
    except Exception as e:
        logging.exception(f"MCP tool {tool_name} failed")
        return f"{tool_name} ишке ашкан жок."

class AitilBankingChatbot:
    def __init__(self):
        self.system_instruction = (
            "Сен банк ассистентисиң. "
            "ЭҢ МААНИЛҮҮ: Эгер суроо боюнча MCP функциясын колдонсо болот — АЛГАЧ MCP функциясын чакыр! "
            "Тек MCP функциясы жок же туура келбесе гана өзүң жооп бер. "
            "Мисалы: 'Канча акча бар?' -> [FUNC_CALL:name=get_balance] "
            "'Акыркы транзакцияларымды көрсөт' -> [FUNC_CALL:name=get_transactions, limit=5] "
            "'1000 сомду Бакытка котор' -> [FUNC_CALL:name=transfer_money, amount=1000, to_name='Бакыт'] "
            "Төмөндө колдонуучунун профили (аты, аккаунттары) берилген — бул маалыматты дайыма эстеп жүр жана статикалык суроолорго (аты, аккаунт түрлөрү) ушул маалыматтан жооп бер. "
            "Баланс, транзакцияларга function calling колдон. Бирок акча которууга тарыхты колдонуу керек.Жоопту кыргызча бер. "
            "Эгерде баланс, транзакциялар жөнүндо информация тарыхта бар болсо дагы, function calling колдонуу керек."
            "МААНИЛҮҮ: Жоопторуңда колдонуучунун атын колдон. Мисалы: 'Ооба, {user_name}, балансыңыз 1000 сом', 'Жакшы, {user_name}, акча которуу ийгиликтүү болду' ж.б. "
            "Колдонуучунун атын жоопторуңда жумшак жана досчолуктуу жол менен колдон. "
            "Функцияны мындай түрдө чакыр: [FUNC_CALL:name=transfer_money, amount=1000, to_name='Айгүл']\n"
            "Доступные функции жана параметрлер:\n"
            f"{generate_function_docs()}\n"
            "user_id кошулат автоматтык түрдө"
        )

    def build_messages(self, conversation_history, user_message, user):
        messages = []
        messages.append({
            "role": "system",
            "content": [{"type": "text", "text": self.system_instruction}]
        })
        if user:
            accounts = ", ".join([f"{a.account_type}" for a in user.accounts])
            profile = (
                f"Профиль:\n"
                f"- Аты: {user.name}\n"
                f"- ID: {user.id}\n"
                f"- Аккаунттар: {accounts if accounts else 'жок'}"
            )
            messages.append({"role": "user", "content": profile})
        if conversation_history:
            for msg in conversation_history[-2:]:
                messages.append({"role": "user", "content": msg["message"]})
                messages.append({"role": "assistant", "content": msg["response"]})
        messages.append({"role": "user", "content": user_message})
        return messages

    async def get_response(self, user_message, conversation_history=None, user=None):
        try:
            messages = self.build_messages(conversation_history, user_message, user)

            payload = {
                "model": "aitil",
                "messages": messages,
                "stream": False,
                "max_tokens": 2000,
                "temperature": 0.5
            }

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(AITIL_API_URL, json=payload)
                response.raise_for_status()
                try:
                    data = response.json()
                except Exception:
                    print("AITIL response text:", response.text)
                    logging.error(f"AitilBot: Non-JSON response: {response.text}")
                    return "Ката: сервер кайтарды неожиданный ответ."
                content = data["choices"][0]["message"]["content"]

                if "[FUNC_CALL:" in content:
                    return await self.handle_function_call(content, user)
                return content
        except Exception as e:
            logging.exception("AitilBot error")
            return "Ката кетти. Кийинчерээк аракет кылыңыз."

    async def handle_function_call(self, text, user):
        try:
            import re
            func_match = re.search(r"\[FUNC_CALL:(.*?)\]", text)
            if not func_match:
                print("[AitilBot] Не найден FUNC_CALL в тексте:", text)
                return text

            raw = func_match.group(1)
            parts = raw.split(",")
            call = {}
            for p in parts:
                key, value = p.strip().split("=")
                call[key.strip()] = value.strip().strip("'").strip('"')

            func_name = call.pop("name")
            call["user_id"] = user.id

            allowed = get_allowed_params(func_name)
            filtered_call = {}
            for k, v in call.items():
                if k in allowed or k == "user_id":
                    filtered_call[k] = cast_param_value(k, v, func_name)

            print(f"[AitilBot] Вызов функции: {func_name} с параметрами: {filtered_call}")
            result = await call_mcp_tool(func_name, **filtered_call)
            print(f"[AitilBot] Ответ функции {func_name}: {result}")
            return result
        except Exception as e:
            logging.exception("handle_function_call failed")
            return "Функцияны чакырууда ката кетти."
