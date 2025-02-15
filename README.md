# NexusDownloader
ai assisted python script for downloading from Nexusmods.com from a simple txt file

## setup environment file
Create an .env file with SESSION_COOKIES set. 
Login to nexusmods and open developer tools (F12), go to network, check for request with session cookie. Copy pasta profit!11
(youre a smart cookie, google it if lost)
Example
```
SESSION_COOKIES="_pk_id.1.3564=98a8871aadb3f24b.1738346509.; nexusmods_session=3064e8eXXXXXXXXXca13ceabfe328280; fwroute=1738522033.652.4360.479674|b295758090068ae543818c1ba2aeea3e; nexusmods_session_refresh=1738522419; __cflb=04dToSn5RVPHhtLrhCv8jYX8fKrnHLeh2ExAzDnBGG; _pk_ref.1.3564=%5B%XXXXXXXX%3A%2F%2Fgithub.com%2F%22%5D; _pk_ses.1.3564=1; cf_clearance=SnYSJygY5nYrwm67jTYaeyQnpApoQLj7PVMJna6nqk0-1738593325-1.2.1.1-gZhh8yvonKfxsUCZo2LHadNZPUEom4v.s_qzruPvH1Zx.YlCzEK9x2SZSTaNjjOAcMrFgPX.MFlPci58hB6gTfBFekzpQI6Hx8UMgFg3J8cypIMWWvRy7u94P1YsQjWG6StTTidncoFepeGyvOrOAKw1pp4a70nDkIE4Ogt1d2iXkLHkGbdNa5bTew8XKgXQflAsBK79X4PHcmqV5IZXEGTX44.XXXXXXXX_TWesTUoe5sm7e5WYlEMt1r4Db9SNX1_CFIHVhC5UqWRXi_myqU9vbmrpvn9BCRgr.QZSno"
LINKS_FILE=output.txt
DOWNLOAD_DIRECTORY=Downloads
OUTPUT_FILE=output.txt
PROCESSED_FILE=processed_output.txt
LOG_DOWNLOAD_PATH=download.log
LOG_SKIP_PATH=skip.log
MAX_THREADS=4
GAME_ID=1704
NEXUS_DOWNLOAD_URL=https://www.nexusmods.com/Core/Libs/Common/Managers/Downloads?GenerateDownloadUrl

```
