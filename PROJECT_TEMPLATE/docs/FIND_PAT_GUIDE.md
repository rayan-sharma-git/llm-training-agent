# How to Find/Create Your PAT (Personal Access Token)

## What is the PAT?

The PAT is a security token used to publish your extension to the VS Code Marketplace. It is **NOT** on GitHub — it's on **Azure DevOps** (Microsoft's free developer platform).

## Important: Sign in with the SAME Microsoft account

You must use the same Microsoft account (email) that you used to create your publisher on the Marketplace.

---

## Method 1: Direct URL (Fastest)

### Step 1: Go directly to the PAT creation page

Open your browser and go to:

```
https://dev.azure.com/users/me/pat
```

This takes you directly to Personal Access Tokens.

### Step 2: Create a new token

1. Click **"+ New Token"** (blue button, top of page)
2. Fill in:
   - **Name:** `VS Code Marketplace Publishing`
   - **Organization:** All accessible organizations
   - **Expiration:** 1 year (or pick a date)
   - **Scopes:** Select "Custom defined" → check **Marketplace** → check **Acquire**
3. Click **"Create"**

### Step 3: Copy the token

A dialog will show your token **ONLY ONCE**. Copy it immediately and save it somewhere safe.

Token format looks like: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Method 2: Navigation Path

### Step 1: Go to Azure DevOps

```
https://dev.azure.com/
```

### Step 2: Sign in

- Use the **same Microsoft account** you used for the Marketplace publisher
- If you don't have an Azure DevOps organization, it will create one automatically (free)

### Step 3: Find User Settings

Look at the **top right corner** of the page:

1. Click on your **profile picture/avatar** (top right)
2. Click **"Personal Access Tokens"** in the dropdown menu

### Step 4: Create new token

Same steps as Method 1 above.

---

## Common Problems & Solutions

### Problem 1: "I don't see Personal Access Tokens"

**Solution:** You need to be signed in to Azure DevOps first. Go to `https://dev.azure.com/` and sign in with your Microsoft account.

### Problem 2: "It takes me to a GitHub login page"

Azure DevOps might ask about GitHub. **Skip this** — use the "Microsoft Account" or "Email" option to sign in.

### Problem 3: "The page is blank"

**Solution:** Try the direct URL: `https://dev.azure.com/users/me/pat`

### Problem 4: "I created a token but it says expired"

**Solution:** When creating the token, set expiration to "1 year" or "Custom defined" with a future date. Never use the minimum expiration.

### Problem 5: "I don't see 'Marketplace' scope"

**Solution:** Scroll down in the Scopes section. Under "Custom defined", find:
- **Marketplace** → check **Acquire**

If you can't find it, click "Show all scopes" (link at bottom of scopes section).

---

## Once You Have the PAT

### Test the token works:

```cmd
cd PROJECT_TEMPLATE\extension
vsce publish --pat YOUR_TOKEN_HERE
```

### If publish fails with "Invalid PAT":

1. Ensure scope = Marketplace: Acquire
2. Ensure same Microsoft account as publisher
3. Try generating a new token (tokens expire)
4. Check token expiration date

### Alternative: Login method (Simpler)

Instead of using PAT directly, you can login once and vsce remembers you:

```cmd
cd PROJECT_TEMPLATE\extension
vsce login your-publisher-name
```

It will ask for a PAT. Enter it once. After that, vsce remembers your login and you can publish with just:

```cmd
vsce publish
```

---

## Quick Steps Summary

1. Go to: `https://dev.azure.com/users/me/pat`
2. Sign in with your Microsoft account
3. Click "+ New Token"
4. Name: `Marketplace Publish`
5. Scope: **Marketplace** → **Acquire**
6. Expiration: 1 year
7. Click "Create"
8. Copy the token (shown only once)
9. Use it with `vsce publish --pat TOKEN`