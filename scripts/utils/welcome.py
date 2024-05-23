import warnings
# Ignore SyntaxWarning
warnings.filterwarnings("ignore", category=SyntaxWarning)
# Print this in orange
print("\033[1m")
art = ["" for _ in range(11)]
art[0] = r"  $$\                                                              "
art[1] = r"  $$ |                                                             "
art[2] = r"$$$$$$\    $$$$$$\  $$$$$$\   $$$$$$\   $$$$$$\                    "
art[3] = r"\_$$  _|  $$  __$$\ \____$$\ $$  __$$\ $$  __$$\                   "
art[4] = r"  $$ |    $$ |  \__|$$$$$$$ |$$ /  $$ |$$ /  $$ |         /        "
art[5] = r"  $$ |$$\ $$ |     $$  __$$ |$$ |  $$ |$$ |  $$ |    (   /_        "
art[6] = r"  \$$$$  |$$ |     \$$$$$$$ |$$$$$$$  |$$$$$$$  | . /_)_/ /_       "
art[7] = r"   \____/ \__|      \_______|$$  ____/ $$  ____/                   "
art[8] = r"                             $$ |      $$ |                        "
art[9] = r"                             $$ |      $$ |                        "
art[10] = r"                             \__|      \__|                       "
print("Starting...", end="\n\n")
for line in art:
    print(line)
print("\033[0m")
