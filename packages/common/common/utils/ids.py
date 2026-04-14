from nanoid import generate

def generate_tenant_id() -> str:
    return f"ten_{generate(size=8)}"


def generate_user_id() -> str:
    return f"usr_{generate(size=8)}"