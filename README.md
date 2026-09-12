# QuickProof

QuickProof is a small app that fixes spelling, extra spacing, capitalisation mistakes, and accidentally doubled punctuation in your writing. It deliberately leaves your grammar and phrasing alone and never adds punctuation of its own. It runs silently in the background. When you press **Ctrl + Shift + /**, it grabs the text you're writing, fixes any errors, and puts the corrected text back. It works in any app - email, chat, browser, notepad, anything with a text field.

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

## Windows on ARM

If your PC runs Windows on ARM (a Snapdragon laptop, or a Windows VM on an Apple Silicon Mac) and you installed the ARM64 build of Python, QuickProof will silently fail to start. The speech library it uses ships only x64 DLLs, which an ARM64 Python cannot load.

After Step 4, run this once from the QuickProof folder:

```
python fix_arm64.py
```

It downloads the official ARM64 NVDA controller client from NV Access, installs it into the speech library, and patches the library so screen readers that have no ARM64 support are skipped instead of crashing. Then carry on with Step 5.

Run it again if you ever upgrade the `accessible_output2` package, because the upgrade will undo the fix.

## Stopping QuickProof

If you ever need to stop it, press **Ctrl + Shift + Esc** to open Task Manager, find **pythonw.exe**, and end the task.

## Mac

The Mac version is `quickproof_mac.py`. It does the same job, but works differently under the hood: it reads the focused text field through the macOS Accessibility API, so it never has to select or cut your text. Native apps get the corrected text written straight back into the field. Web-based apps such as Discord, Slack, browsers, and Mail's composer are updated with a paste, with your clipboard saved and restored around it. If you leave the text field or keep typing while it is waiting for the correction, nothing is replaced.

The hotkey is **fn + /**.

### What you need

- Python 3 (Homebrew's is fine).
- Karabiner-Elements, installed and running. It provides the hotkey.
- An OpenRouter API key, as in Step 2 above.

### Setup

1. Open Terminal and go to the QuickProof folder, for example `cd ~/Documents/QuickProof`
2. Run `bash setup_mac.sh`. It creates a private Python environment, asks for your API key if it is not already in the `OPENROUTER_API_KEY` environment variable, adds the fn + / rule to Karabiner-Elements, and runs a test correction so you know the key works.
3. Click into any text field and press fn + /. The first time, macOS shows an Accessibility permission dialog. Open System Settings, Privacy and Security, Accessibility, and turn on the item it names, expected to be `karabiner_console_user_server`. Press fn + / again.

### Sounds

QuickProof never speaks. It only plays a sound.

- **Breeze sound** (the file is called Blow): the text was replaced, or it was already correct.
- **Boop sound** (the file is called Basso): nothing was replaced. The log says why: no text found, text too long, correction failed, or the text field changed while waiting.

### Checking and troubleshooting

- `~/.local/share/quickproof/venv/bin/python3 quickproof_mac.py --check` reports whether the key and permissions are in place.
- `~/.local/share/quickproof/venv/bin/python3 quickproof_mac.py --test "some txet"` corrects the given text and prints it, without touching any app.
- Every press writes a line to `~/Library/Logs/QuickProof.log` saying which app it saw and which path it took.
- Your API key lives in `~/.config/quickproof/api_key`. Karabiner does not pass your shell's environment variables to the script, which is why it is stored in a file.

### Removing

Open Karabiner-Elements, go to Complex Modifications, and remove the QuickProof rule. Then delete `~/.local/share/quickproof` and `~/.config/quickproof`.
