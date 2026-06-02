from nanoid import generate

def generate_profile_id() -> str:
    return f"cp_{generate(size=8)}"

def generate_profile_version_id() -> str:
    return f"cpv_{generate(size=8)}"

def generate_tool_id() -> str:
    return f"tol_{generate(size=8)}"

def generate_regulation_id() -> str:
    return f"reg_{generate(size=8)}"

def generate_regulation_version_id() -> str:
    return f"rgv_{generate(size=8)}"

def generate_rule_id() -> str:
    return f"rul_{generate(size=8)}"

def generate_rule_version_id() -> str:
    return f"rlv_{generate(size=8)}"