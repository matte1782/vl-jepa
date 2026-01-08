# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **DO NOT** open a public issue
2. Email security concerns to the maintainer
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a detailed response within 7 days.

## Security Measures

### Branch Protection
- `main`/`master` branches are protected
- Force pushes and deletions are blocked
- All changes require Pull Request review
- Status checks must pass before merge

### CI/CD Security
- All PRs run automated security scans
- Dependencies checked with `pip-audit`
- Code scanned with `bandit`
- No secrets in repository (`.env` files gitignored)

### Dependencies
- Dependabot enabled for automatic security updates
- Regular dependency audits
- Pinned versions for reproducibility

## Security Best Practices for Contributors

1. Never commit secrets, API keys, or credentials
2. Use environment variables for sensitive configuration
3. Keep dependencies updated
4. Follow secure coding guidelines
5. Report suspicious activity immediately

## Acknowledgments

We appreciate responsible disclosure from security researchers.
