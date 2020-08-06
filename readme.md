assets contains assets necessary to operate, program will not work without these files
extras contains test file, unused code, and .sketch file of main ui design does not need to be inclided in install

use pyinstaller to compile into executable and inno installer to compile into installer executable witch is releasable.
for pyinstaller to not fail, only include the main scrypt and the assets folder and LICENSE.txt.

icon for installer located in root/extras
