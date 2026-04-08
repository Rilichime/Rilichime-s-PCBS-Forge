### 2.1.0  `Major Update` Add Parts From Screenshot, Run Program Objective, UI Changes, Bug Fixes
- Complete rewrite of auto-build feature to hopefully work better with 3DMark objectives.
- Added RAM & storage min size inputs for Jobs
- Added Run Program to job details. This will provide a warning if the user adds parts that do not meet the specs required to run the program. I have utilized the data provided on the [PCBS Wiki](https://pcbuildingsim.fandom.com/wiki/Will_it_Run%3F) page.
- Added the new screenshot to text feature. This feature will take screenshots, allow you to crop to just the part names, and automatically add those parts to either the currently selected job or currently selected inventory (used parts / new parts).
- Changed UI colors, increased some text sizes, added color indicators for part categories (based on the in-game colors), adjusted accessibility settings to just two options (default and large), and added icons to various parts of the UI.
- Updated screenshots to reflect the new UI changes.
- Changed Motherboard to MOBO, CPU Cooler to Cool, Case Fans to Fan, and Storage to Drive.

### 2.0.0 `Major Update` Complete Recode
- Complete recode of the entire program.

### 1.1.0 `Minor Update` Accessibility & UI Improvements
- The drop-down boxes for selecting jobs, builds, and text size have been updated for improved visibility. As well, these fields now scale size properly when changing accessability settings.
- The inventory now scales text size properly when selecting larger font sizes.
- Cleaned up some redundant code, standardized the error logging to use logger consistently instead of print, removed live update feature for configs, and changed all references to PCBuilderApp to Rilichimes-PCBS-Forge.
- Added an accessability config file that will save user preferences instead of returning to default each time the program is loaded.
- Filters have been adjusted slightly. Columns that have numeric values now have an input for min and max thresholds. 

### 1.0.0 — Initial release.
First release of the program.
