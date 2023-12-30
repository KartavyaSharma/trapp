import argparse
import json
import pathlib
import os
import sys

# Make constants accessible to utils
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../../../..")

import constants


def generate_code(
    name: str, desc: str, homepage: str, url: str, sha256: str, dependencies: any
):
    header = f"""class {name.capitalize()} < Formula
"""

    metadata = f"""
    desc "{desc}"
    homepage "{homepage}"
    url "{url}"
    sha256 "{sha256}"

"""

    depends_on = ""
    for dep in dependencies["general"]:
        depends_on += f'    depends_on "{dep}"\n'

    conditional_darwin = """
    if OS.mac?
"""

    conditional_darwin_depends_on = ""
    for dep in dependencies["darwin"]:
        conditional_darwin_depends_on += f'        depends_on "{dep}"\n'

    conditional_linux = """
    elsif OS.linux?
"""

    conditional_linux_depends_on = ""
    for dep in dependencies["linux"]:
        conditional_linux_depends_on += f'        depends_on "{dep}"\n'

    conditional_footer = """
    end
"""

    conditional = (
        conditional_darwin
        + conditional_darwin_depends_on[: -len("\n")]
        + conditional_linux
        + conditional_linux_depends_on[: -len("\n")]
        + conditional_footer
    )

    install = """
    def install
        libexec.install Dir["*"]

        (bin/"{name}").write <<~EOS
            #!/bin/bash
            exec "#{libexec}/start.sh" "$@"
        EOS
        bin.install_symlink "#{libexec}/start.sh" => "#{name}"
    end
"""

    test = """
    test do
        system "{name}", "--help"
    end
"""

    footer = """
end
"""

    return header + metadata + depends_on + conditional + install + test + footer


def get_config():
    # Convert json file into a dictionary from the formula config file
    with open(constants.FORMULA_CONFIG_PATH, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sha", help="SHA256 value")

    args = parser.parse_args()

    config_object = get_config()

    dependencies = {
        "general": config_object["dependencies"],
        "darwin": config_object["darwin"]["dependencies"],
        "linux": config_object["linux"]["dependencies"],
    }

    formula = generate_code(
        config_object["metadata"]["name"],
        config_object["metadata"]["description"],
        config_object["metadata"]["homepage"],
        config_object["metadata"]["url"],
        args.sha,
        dependencies,
    )

    formula_path = f"{constants.FORMULA_PATH}/{config_object['metadata']['name']}.rb"
    # Check if formula path exists
    if not os.path.exists(constants.FORMULA_PATH):
        os.makedirs(constants.FORMULA_PATH)
    
    with open(formula_path, "w") as f:
        f.write(formula)

    print(f"Generated formula for {config_object['metadata']['name']}")
