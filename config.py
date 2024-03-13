import configparser
import os

from version import __version__
from dotenv import load_dotenv

load_dotenv()


class FlaskMonitoringDashboardConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

    def write(self, fp):
        if self._defaults:
            fp.write("[%s]\n" % configparser.DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s=%s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key == "__name__":
                    continue
                if (value is not None) or (self._optcre == self.OPTCRE):
                    key = "=".join((key, str(value).replace('\n', '\n\t')))
                fp.write("%s\n" % (key))
            fp.write("\n")


def build_config_file():
    # Initialize the ConfigParser object
    config = FlaskMonitoringDashboardConfigParser()

    # Read the configuration file
    config.read('config.template.cfg')

    # Update the values in the configuration file
    def overwrite(section: str, options: list[str]):
        for option in options:
            config[section][option] = os.getenv(
                option, config.get(section, option))


    overwrite('authentication', ['USERNAME', 'PASSWORD', 'SECURITY_TOKEN'])

    # Update the app version
    config['dashboard']['APP_VERSION'] = __version__

    # Write the updated values to the config file
    with open('config.cfg', 'w') as configfile:
        config.write(configfile)
