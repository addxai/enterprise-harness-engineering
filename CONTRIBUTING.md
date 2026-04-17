# Contributing to Enterprise Harness Engineering Skills

Thank you for your interest in contributing! This project follows the Agent Skills Specification.

## How to Contribute

### Adding a New Skill

1. Fork this repository
2. Create a new directory under `skills/` with your skill name (lowercase, hyphens only)
3. Add a `SKILL.md` with proper YAML frontmatter:

```yaml
---
name: your-skill-name
description: What it does and when to use it. Include trigger keywords.
---
```

4. Keep `SKILL.md` under 500 lines. Use `references/` for detailed documentation.
5. Submit a merge request

### Skill Quality Checklist

- [ ] `name` field matches directory name
- [ ] `description` includes both "what" and "when"
- [ ] No company-specific information (internal URLs, account IDs, product names)
- [ ] No hardcoded secrets or credentials
- [ ] Examples use generic placeholders (`example.com`, `<your-value>`)
- [ ] All referenced files exist (no broken links)

### Improving Existing Skills

- Fix typos, improve examples, add references
- Keep changes focused — one improvement per MR
- Test that the skill still works after your changes

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
