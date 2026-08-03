# VS Code Marketplace Deployment Guide

## Question: Is it free to deploy on VS Code Marketplace?

**Answer: YES — Publishing to the VS Code Marketplace is 100% free.**

Microsoft does not charge any fees for publishing extensions to the Visual Studio Code Marketplace.

## Complete Deployment Guide

### Prerequisites (Free)

1. **Microsoft Azure DevOps Account** — Free
   - Sign up at: https://azure.microsoft.com/free/
   - Used for publishing pipeline
   - No credit card required for free tier

2. **GitHub Account** — Free
   - Required for repository
   - Public or private repos both work

3. **VS Code** — Free
   - Download from: https://code.visualstudio.com/

4. **Node.js** — Free
   - Version 18+ required
   - Download from: https://nodejs.org/

5. **vsce (VS Code Extension Manager)** — Free
   ```bash
   npm install -g @vscode/vsce
   ```

### Publishing Costs

| Item | Cost | Notes |
|------|------|-------|
| **Marketplace Listing** | **FREE** | No listing fees |
| **Extension Hosting** | **FREE** | Microsoft hosts extensions |
| **Downloads** | **FREE** | Unlimited downloads |
| **Updates** | **FREE** | Unlimited updates |
| **Azure DevOps Pipeline** | **FREE** | For public repos (unlimited minutes) |
| **Domain for icon/screenshots** | Optional | Can use free GitHub Pages or Imgur |

**Total Cost: $0**

### Step-by-Step Publishing Process

#### Step 1: Prepare Your Extension

Ensure these files exist in `extension/`:

```
extension/
├── package.json          # Extension manifest
├── README.md             # Marketplace description
├── CHANGELOG.md          # Version history
├── LICENSE               # License file
├── icon.png              # 128x128 extension icon
└── .vscodeignore         # Files to exclude from package
```

**Example package.json:**
```json
{
  "name": "llm-training-agent",
  "publisher": "your-publisher-name",
  "version": "1.0.0",
  "description": "AI-powered assistant for LLM fine-tuning projects",
  "engines": {
    "vscode": "^1.74.0"
  },
  "categories": ["Machine Learning", "Other"],
  "keywords": ["llm", "fine-tuning", "machine-learning", "ai"],
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/llm-training-agent"
  },
  "license": "MIT"
}
```

#### Step 2: Create Publisher Account

1. Go to https://marketplace.visualstudio.com/manage
2. Sign in with Microsoft account (free)
3. Click "Create Publisher"
4. Enter publisher name and ID (e.g., "ml-engineer-tools")
5. Verify email (free)

**Cost:** $0

#### Step 3: Create Personal Access Token (PAT)

1. Go to https://dev.azure.com/
2. Click "User Settings" → "Personal Access Tokens"
3. Create new token with scopes:
   - **Marketplace** → "Acquire", "Manage"
4. Copy token (shown only once!)

**Cost:** $0

#### Step 4: Package Extension

```bash
cd extension
vsce package
```

This creates `llm-training-agent-1.0.0.vsix` (your extension package).

**Cost:** $0

#### Step 5: Publish to Marketplace

```bash
vsce publish --pat YOUR_PERSONAL_ACCESS_TOKEN
```

Or publish the VSIX file:
```bash
vsce publish --packagePath llm-training-agent-1.0.0.vsix --pat YOUR_PAT
```

**Cost:** $0

#### Step 6: Verify Publication

1. Go to https://marketplace.visualstudio.com/manage
2. Your extension should appear as "Published"
3. View at: https://marketplace.visualstudio.com/items?itemName=your-publisher.llm-training-agent

**Cost:** $0

### Marketplace Requirements (All Free)

| Requirement | Cost | How to Get |
|------------|------|-----------|
| Publisher Account | Free | Sign up at marketplace.visualstudio.com |
| Azure DevOps Account | Free | Sign up at azure.microsoft.com/free |
| Personal Access Token | Free | Generate in Azure DevOps settings |
| Extension Icon | Free | Create 128x128 PNG yourself |
| Screenshots | Free | Use built-in VS Code screenshot tool |
| README.md | Free | Write documentation |
| License | Free | Use MIT, Apache, or other open-source license |

### Optional: Automated Publishing with GitHub Actions (Free)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to VS Code Marketplace

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '18.x'
      
      - run: npm install
      
      - run: npm run compile
      
      - run: vsce package
      
      - uses: HaaLeo/publish-vscode-extension@v1
        with:
          pat: ${{ secrets.VSCODE_MARKETPLACE_TOKEN }}
          registryUrl: 'https://marketplace.visualstudio.com'
```

**Setup:**
1. Go to GitHub repo → Settings → Secrets
2. Add secret: `VSCODE_MARKETPLACE_TOKEN` = your PAT
3. Create a release → extension auto-publishes

**Cost:** $0 (GitHub Actions free for public repos)

### Optional Costs (Not Required)

| Item | Cost | Why You Might Need It |
|------|------|----------------------|
| Custom domain | $10-15/year | For documentation website |
| Professional icon design | $0-50 | Can make yourself for free |
| Screenshot hosting | $0 | Use GitHub or Imgur for free |
| CI/CD for private repo | $0-4/month | Public repos are free |
| Code signing certificate | $0-200/year | Optional for extra security |

**Minimum required: $0**

### Marketplace Policies (Free to Comply)

#### Requirements:
1. **No malicious code** — Self-explanatory
2. **No privacy violations** — Don't steal user data
3. **No copyright infringement** — Use your own code/assets
4. **Functional extension** — Must actually work
5. **Open source license** — Include LICENSE file

#### Prohibited (Free to Avoid):
- ❌ Cryptocurrency mining
- ❌ Data harvesting without consent
- ❌ Affiliate link spam
- ❌ Malware/adware
- ❌ Copying other extensions

**Your extension is compliant:**
- ✅ Analyzes user projects locally
- ✅ No data harvesting
- ✅ Open source (MIT license)
- ✅ Functional and tested
- ✅ Real value to users

### Monetization Options (Optional)

The marketplace doesn't charge you, but you can choose to monetize:

| Model | Cost to User | Your Revenue |
|-------|-------------|--------------|
| **100% Free** | $0 | $0 (community contribution) |
| **Freemium** | Free tier + paid Pro | Subscription revenue |
| **Donations** | Free + optional donation | Voluntary support |
| **Sponsorship** | Free + sponsored by company | Sponsorship deal |
| **Paid** | One-time or subscription | Revenue per install |

**Recommendation:** Start free, add optional donations/sponsorship later.

### Examples of Free Extensions on Marketplace

Many popular extensions are free:
- **Prettier** — Code formatter (free)
- **ESLint** — Linter (free)
- **GitLens** — Git enhancement (free + paid Pro)
- **Material Icon Theme** — Icons (free)
- **Python** — Python language support (free)
- **C/C++** — C++ support (free)

**Your extension fits the "free" model perfectly.**

## FAQ

### Q: Is there a review process?
**A:** Yes, Microsoft reviews extensions. Takes 1-3 business days. Free.

### Q: Can I update my extension later?
**A:** Yes, unlimited updates for free.

### Q: What if I need to unpublish?
**A:** You can unpublish anytime. Free.

### Q: Are there usage limits?
**A:** No limits on downloads or users. Free.

### Q: Can I publish a private extension?
**A:** Yes, for your organization only. Requires Azure DevOps. Free for orgs.

### Q: Do I need a website?
**A:** No, but README.md serves as documentation. Free.

### Q: What about support?
**A:** Use GitHub Issues (free) or Discord (free).

## Final Answer

**"Is it free to deploy on VS Code Marketplace?"**

**YES. 100% free.**

- ✅ Publishing: Free
- ✅ Hosting: Free
- ✅ Downloads: Free
- ✅ Updates: Free
- ✅ Reviews: Free
- ✅ Listing: Free

**Only cost:** Your time to build the extension.

**Optional costs:** Domain name ($10/year), professional icon ($0-50), but both have free alternatives.

**Total minimum cost: $0**

You can publish today for free and start helping ML engineers worldwide.