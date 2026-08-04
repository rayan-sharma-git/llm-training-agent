# Azure Free Tier Explained

## Question: "Try Azure for free — how is this free?"

## Answer: Azure gives you $200 free credit + free services, no credit card required for the free tier.

---

## What You Get Free

### 1. $200 Free Credit (30 Days)

- **What:** $200 credit to use on any Azure service
- **Duration:** 30 days from signup
- **Use it for:** Testing, learning, small projects
- **After 30 days:** If you don't upgrade, you keep the free services below

### 2. 12 Months of Free Services

After the $200 credit expires, you get 12 months of free services:

| Service | Free Amount |
|---------|-------------|
| Virtual Machines | 750 hours/month (B1s) |
| Storage | 5 GB |
| Databases | 250 GB SQL |
| Functions | 1M requests/month |
| App Service | 10 web apps |
| DevOps | Unlimited (free) |

### 3. Always-Free Services (No Expiry)

These are free forever:

| Service | Free Amount |
|---------|-------------|
| Azure DevOps | Unlimited (this is what we use for publishing) |
| VS Code Marketplace | Free publishing |
| GitHub | Free for public repos |
| Azure Functions | 1M requests/month |
| Azure Container Registry | 1 container instance |

---

## Why We Need Azure DevOps (Not Azure Cloud)

**Important distinction:**

- **Azure DevOps** = Free developer platform for CI/CD, publishing extensions
- **Azure Cloud** = Paid cloud services (VMs, databases, etc.)

**We only need Azure DevOps** for publishing your VS Code extension. It's 100% free with no credit card.

---

## How to Sign Up (Free)

### Option A: Just Azure DevOps (Recommended)

1. Go to: https://dev.azure.com/
2. Sign in with your Microsoft account
3. That's it — you have Azure DevOps for free
4. No credit card needed
5. Create PAT → publish extension

### Option B: Full Azure Free Account

1. Go to: https://azure.microsoft.com/free/
2. Click "Start free"
3. Sign in with Microsoft account
4. **Optional:** Add credit card (for $200 credit)
5. **OR:** Skip credit card — you still get free services

**Note:** You can use Azure DevOps WITHOUT the $200 credit. The credit is only for cloud services.

---

## What We Actually Use

For publishing your extension, we use:

1. **Azure DevOps** — Free, no credit card
2. **Personal Access Token (PAT)** — Free to create
3. **VS Code Marketplace** — Free to publish

**Total cost: $0**

---

## Common Questions

### Q: Do I need a credit card?
**A:** No. Azure DevOps is free without a credit card. The $200 credit requires a card but is optional.

### Q: Will I be charged after 30 days?
**A:** No. If you don't upgrade to paid, you keep the free services. You're never charged without consent.

### Q: What's the difference between Azure and Azure DevOps?
**A:**
- **Azure** = Cloud computing (VMs, databases) — paid
- **Azure DevOps** = Developer tools (CI/CD, publishing) — free

### Q: Can I publish my extension without Azure?
**A:** No. The PAT (used for publishing) comes from Azure DevOps. It's free.

---

## Summary

| Item | Cost | Credit Card Needed |
|------|------|-------------------|
| Azure DevOps | Free | No |
| PAT (publishing token) | Free | No |
| VS Code Marketplace | Free | No |
| $200 Azure credit | Free | Optional |
| 12-month free services | Free | Optional |

**For your extension: $0, no credit card required.** 