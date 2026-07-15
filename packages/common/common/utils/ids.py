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

def generate_assessment_id() -> str:
    return f"asm_{generate(size=8)}"

def generate_gap_id() -> str:
    return f"gap_{generate(size=8)}"

def generate_ropa_id() -> str:
    return f"rop_{generate(size=8)}"

def generate_policy_id() -> str:
    return f"pol_{generate(size=8)}"

def generate_policy_version_id() -> str:
    return f"ver_{generate(size=8)}"

def generate_processor_id() -> str:
    return f"prc_{generate(size=8)}"

def generate_breach_id() -> str:
    return f"brc_{generate(size=8)}"

def generate_dsar_id() -> str:
    return f"dsr_{generate(size=8)}"

def generate_evidence_id() -> str:
    return f"evd_{generate(size=8)}"