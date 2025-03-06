# Final Testing & Security Audits for AegisLang

import hashlib

class AegisLangSecurityAudit:
    """Performs security checks on AegisLang compiler, standard library, and AI-generated code."""

    def __init__(self, code_samples):
        self.code_samples = code_samples

    def detect_insecure_patterns(self):
        """Scans for common security vulnerabilities in AI-generated code."""
        insecure_patterns = ["eval(", "exec(", "system(", "subprocess.call("]
        found_issues = []

        for sample in self.code_samples:
            for pattern in insecure_patterns:
                if pattern in sample:
                    found_issues.append(f"Potential security risk: Found '{pattern}' in code.")

        return found_issues if found_issues else ["No security vulnerabilities detected."]

    def integrity_check(self, code):
        """Generates a hash of the AI-generated code for integrity validation."""
        return hashlib.sha256(code.encode()).hexdigest()

    def run_audit(self):
        """Runs all security and integrity tests."""
        audit_results = {
            "Security Scan": self.detect_insecure_patterns(),
            "Code Integrity Hash": [self.integrity_check(sample) for sample in self.code_samples],
        }
        return audit_results

if __name__ == "__main__":
    # Example usage
    generated_enterprise_code = "module ECommerce..."
    optimized_ai_code = "module ECommerce optimized..."
    audit = AegisLangSecurityAudit([generated_enterprise_code, optimized_ai_code])
    results = audit.run_audit()
    print("Security Scan:", results["Security Scan"])
    print("Integrity Hashes:", results["Code Integrity Hash"])