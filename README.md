[![Text](https://github.com/Rilichime/Rilichime-s-PCBS-Forge/blob/main/Banner.png?raw=true)](https://github.com/Rilichime/Rilichime-s-PCBS-Forge/blob/main/Banner.png?raw=true)

### A desktop application for PC Building Simulator that helps you manage inventory, create builds, track jobs, and check compatibility.
---
### <img src="https://cdn-icons-png.flaticon.com/128/9797/9797618.png" width="25"> About PCBS-Forge<br><br>
PCBS-Forge is a Python program built to be used during your PCBS playthroughs. It was made in Windsurf using Kimi K2.5, Kimi K2.6, and Opus 4.6. 

---

### <img src="https://cdn-icons-png.flaticon.com/128/616/616489.png" width="25"> Features<br><br>

**UI**
- **Dark theme with larger text options**, featuring easy-to-read fonts and 2x text size option for accessibility
- **Quick copy for part names** — double-click to copy full part names, then paste in-game with Ctrl + V
- **Clean, intuitive design** that’s easy to navigate and understand
- **Settings tab** that allows you to customize your PCBS-Forge experience

**Inventory**
- **Separate tabs** for new parts and used parts
- **Live part search** with suggestions, allowing you to quickly find and add parts to your inventory  
- **Advanced sorting and filtering** based on a wide range of specifications  
- **HEM mod support** — enable and configure HEM parts directly in the Settings tab
- **Screenshot parts** to easily bulk add parts to inventory.
- **Delete all button** in case you need to remove all parts

**Builds & Jobs**
- **Job tracking system** to help you manage and organize parts for each job  
- **Compatibility checks** that warn you when selecting incompatible parts  
- **Inferior parts warning** that alerts you if a customer build has an inferior part  
- **Budget tracking** that calculates total costs and remaining funds
- **Completion management** — mark builds or jobs as complete to automatically remove used parts from inventory  
- **3DMark score and PC value previews** to optimize builds for PCBay selling
- **Builds use only used parts, Jobs use only new parts** for maximum profits
- **Bonus objective tracker** for cables, viruses, dust removal, and brand requirements  
- **Smart job assistance** that shows replaceable parts and locks restricted slots

**Auto Build Feature**
- **Chooses parts** based on which is chepest while meeting requirements
- **Fulfills all criteria** such as RAM size, 3DMark, brand, program
- **Ensures compatability** and checks that new parts are not inferior
- **Replaces all possible parts** while respecting budget
- **Budget-aware pruning** based on priority list in Settings tab
- **Marks parts to purchase** so you know what you need to buy

---

<details>
  <summary>Screenshots (Click To Show/Hide)</summary>
<img src="https://github.com/Rilichime/Rilichime-s-PCBS-Forge/blob/main/Screenshot%20A.png"><br><img src="https://github.com/Rilichime/Rilichime-s-PCBS-Forge/blob/main/Screenshot%20B.png"><br><img src="https://github.com/Rilichime/Rilichime-s-PCBS-Forge/blob/main/Screenshot%20C.png"><br><img src="https://github.com/Rilichime/Rilichime-s-PCBS-Forge/blob/main/Screenshot%20D.png"><br>


</details>

---

### <img src="https://cdn-icons-png.flaticon.com/128/6121/6121171.png" width="25"> Antivirus<br><br>

Some Antivirus may flag this as suspicious due to PyInstaller packing. This is a known false positive. The app is not harmful, and it's 100% open source - you can inspect the code yourself.
Options: 1) Run the EXE and click "Run anyway" in Windows Defender, or 2) Run from source

---

### <img src="https://cdn-icons-png.flaticon.com/128/5832/5832416.png" width="25"> User Guide<br><br>

**Download & Run Program**
1. Download the latest release of this program [here](https://github.com/Rilichime/Rilichime-s-PCBS-Forge/releases) (under Assets, you should see `PCBS-Forge.exe`)
2. Find the file on your computer (check the Downloads folder if you can't find it)
3. Run the .exe file
4. If Windows Defender interferes, find where it says More Options and click Run Anyway.
5. The program is now ready for your use

**Download & Run Source Code**
1. Install Python (Version 3.10+) from [python.org](https://www.python.org/downloads/)
2. Download source zip [here](https://github.com/Rilichime/Rilichime-s-PCBS-Forge/releases) (under Assets, you should see `PCBS-Forge-2.0.0.zip`)
3. Run command pip install -r requirements.txt
4. Run file python main_entry.py

**Adding Parts To Inventory Via Search**
1. In the Used Parts tab or the New Parts tab, click the Search tab at the top
2. Type part of a part name (e.g., "corsair 120mm")
3. Double-click suggestions in the list
4. Each part becomes an individual entry in the inventory

**Adding Parts Via Screenshot**
1. Take a screenshot in-game using the PrtScn key. You can screenshot the list of customer parts from the PC, the list of parts in your cart in the shop, or from your inventory (make sure to filter New only or Used only)
2. Find the "Screenshot" tab (inside the Used Parts, New Parts, and Jobs tabs)
3. Click the first button (blue button) to paste your screenshot
4. A crop window will appear. Crop the screenshot so that just the names of parts are inside the red lines
5. Continue adding and cropping images (up to 50 at a time)
6. Once all images are added, click the second button (green button)
7. A pop-up with a list of what text was detected and what part was added will appear. Check this to ensure it is correct
8. The parts should now be listed in the inventory

**Creating Builds / Jobs**
1. Switch to the Builds or Jobs tab
2. Click the first button (green button) and enter the name of the build/customer
3. Go back to Used Parts (for builds) or New Parts (for jobs)
4. Click the green button (first column) for parts you want to add
5. Parts will be automatically placed in appropriate slots

**Completing Builds / Jobs**
1. Select a job or build from the drop-down in the Jobs or Builds tab
2. Click the last button (blue button)
3. Confirm the action
4. Included parts are removed from the parts inventory and the build/job is deleted

**Using Auto Build**
1. Select or create a job in the Jobs tab
2. Enter Level & Budget information
3. Select Job Details and fill in Bonus Objectives if applicable
5. Fill in Customer Original Parts (if applicable)
6. Click the Auto-Build tab, then click the blue button
7. Best build will be displayed in the Player Chosen Parts or New PC Build section

---

### <img src="https://cdn-icons-png.flaticon.com/128/6121/6121171.png" width="25"> Bug Reports<br><br>

If you encounter any issues while using PCBS-Forge, please let me know! You can submit an issue [here](https://github.com/Rilichime/Rilichime-s-PCBS-Forge/issues) or contact me on Discord @Chimeria.
You may also contact me (via Discord or the link above) with any questions or feature requests.

---

### <img src="https://cdn-icons-png.flaticon.com/128/4955/4955340.png" width="25"> Credits<br><br>
- CSV data compiled from PUC_Snakeman's spreadsheet [Parts & Unlock Levels](https://steamcommunity.com/sharedfiles/filedetails/?id=1798336403)
- Star icon made by Freepik from https://www.flaticon.com/free-icon/star_616489
- Question icon made by riajulislam from https://www.flaticon.com/free-icon/question-mark_9797618
- Hands icon made by Smashicons from https://www.flaticon.com/free-icon/hands_4955340
- Book icon made by popo2021 from https://www.flaticon.com/free-icon/stack-of-books_5832416
- Alert icon made by DinosoftLabs from https://www.flaticon.com/free-icon/alert_6121171
- Bug icon made by Freepik from https://www.flaticon.com/free-icon/bed-bug_1850178
