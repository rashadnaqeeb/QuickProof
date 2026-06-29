# QuickProof

QuickProof is a small Windows app that fixes spelling, extra spacing, and capitalisation mistakes in your writing. It deliberately leaves your grammar and phrasing alone. It runs silently in the background. When you press **Ctrl + Shift + /**, it grabs the text you're writing, fixes any errors, and puts the corrected text back. It works in any app - email, chat, browser, notepad, anything with a text field.

## Step 1: Install Python

You need Python installed on your computer. If you're not sure whether you have it, open the Start menu, type **cmd**, and open Command Prompt. Then type:

```
python --version
```

If you see a version number like `Python 3.12.4`, you're good — skip to Step 2.

If you get an error, you need to install Python:

1. Go to **python.org/downloads**
2. Click **Download Python** to get the latest version
3. Run the installer
4. **Important:** On the first screen of the installer, make sure the option **"Add Python to PATH"** is enabled before clicking Install

Close and reopen Command Prompt after installing.

## Step 2: Get an OpenRouter API Key

QuickProof uses an online service called OpenRouter to check your text. You need to create an account and get a key.

1. Go to **openrouter.ai**
2. Click **Sign In** and create an account (you can use Google to sign in)
3. Once logged in, go to **Keys** in your account menu
4. Click **Create Key**, give it a name, and confirm
5. Copy the key it gives you - you will not be able to retrieve it again, so don't close the page until you've completed the next step

OpenRouter charges per request, but QuickProof uses a small, cheap model, so typical use costs a tiny fraction of a cent per correction. You will need to add a small amount of credit to your OpenRouter account for it to work.

## Step 3: Save Your API Key

You need to tell Windows your API key so QuickProof can use it.

1. Open the Start menu and type **cmd**
2. Right-click **Command Prompt** and choose **Run as administrator**
3. Type the following command, replacing `your-key-here` with the key you copied:

```
setx OPENROUTER_API_KEY "your-key-here" /M
```

4. It should respond with **"SUCCESS: Specified value was saved."**
5. Close Command Prompt

## Step 4: Install QuickProof's Dependencies

QuickProof needs a few extra Python packages to work.

1. Open a **new** Command Prompt (not the old one - it won't have the API key yet)
2. Navigate to the folder where you saved QuickProof. For example, if you saved it in a folder called QuickProof on your desktop, type:

```
cd Desktop\QuickProof
```

3. Then type:

```
pip install -r requirements.txt
```

Wait for it to finish. It will output messages about packages being downloaded and installed.

## Step 5: Run QuickProof

Double-click the **quickproof.pyw** file. No window will open - that's normal. It's running silently in the background.

Now click into any text field and type something. Press **Ctrl + Shift + /** and wait a moment. You'll hear a high-pitched beep when the correction is done.

- **High beep** - text was corrected successfully
- **Low beep** - something went wrong, or there was no text to check

## Step 6: Make It Start Automatically

So you don't have to run QuickProof manually every time you restart your computer:

1. Press **Win + R** on your keyboard (hold the Windows key and tap R)
2. Type **shell:startup** and press Enter — this opens your startup folder
3. Copy your **quickproof.pyw** file into that folder

QuickProof will now start automatically whenever you log in to Windows. It may take a minute or so after login before it's ready.

## Stopping QuickProof

If you ever need to stop it, press **Ctrl + Shift + Esc** to open Task Manager, find **pythonw.exe**, and end the task.
