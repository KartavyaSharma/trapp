import warnings
# Ignore SyntaxWarning
warnings.filterwarnings("ignore", category=SyntaxWarning)
# Print this in orange
print("\033[1m")
art = ["" for _ in range(11)]
art[0] = "  $$\                                                              "
art[1] = "  $$ |                                                             "
art[2] = "$$$$$$\    $$$$$$\  $$$$$$\   $$$$$$\   $$$$$$\                    "
art[3] = "\_$$  _|  $$  __$$\ \____$$\ $$  __$$\ $$  __$$\                   "
art[4] = "  $$ |    $$ |  \__|$$$$$$$ |$$ /  $$ |$$ /  $$ |         /        "
art[5] = "  $$ |$$\ $$ |     $$  __$$ |$$ |  $$ |$$ |  $$ |    (   /_        "
art[6] = "  \$$$$  |$$ |     \$$$$$$$ |$$$$$$$  |$$$$$$$  | . /_)_/ /_       "
art[7] = "   \____/ \__|      \_______|$$  ____/ $$  ____/                   "
art[8] = "                             $$ |      $$ |                        "
art[9] = "                             $$ |      $$ |                        "
art[10] = "                             \__|      \__|                       "
print("Starting...", end="\n\n")
for line in art:
    print(line)
print("\033[0m")
