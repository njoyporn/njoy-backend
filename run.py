from backend_shared.api.router import api
from backend_shared.configurator import Configurator
from backend_shared.database import setup as dbSetup
from backend_shared.security import setup as securitySetup
from backend_shared.api.utils import Utils

if __name__ == "__main__":
    configurator = Configurator()
    configurator.load_config()
    security_setup = securitySetup.Setup(configurator.config)
    security_setup.setup_keys()
    db_setup = dbSetup.Setup(configurator.config)
    db_setup.init_db()
    utils = Utils(configurator.config)
    utils.verwaltung_create_default_admin_account()

    if configurator.config["api"]["cors_enabled"]:
        from flask_cors import CORS
        CORS(api, origins=configurator.config["api"]["allowed_domains"])
    api.run(debug=True, host=configurator.config["api"]["hostname"], port=configurator.config["api"]["port"])
