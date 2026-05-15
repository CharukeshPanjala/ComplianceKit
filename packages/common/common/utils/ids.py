from nanoid import generate

def generate_tenant_id() -> str:
    return f"ten_{generate(size=8)}"

def generate_user_id() -> str:
    return f"usr_{generate(size=8)}"

def generate_profile_id() -> str:
    return f"cp_{generate(size=8)}"

def generate_profile_version_id() -> str:
    return f"cpv_{generate(size=8)}"

def generate_tool_id() -> str:
    return f"tol_{generate(size=8)}"