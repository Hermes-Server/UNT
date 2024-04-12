# Hermes
def getHost():
    #return "127.0.0.1" # Development
    return "aam-ntcohort.eng.unt.edu" # Production
    
def getPort():
    #return "4443" # Development
    return "443" # Production

def hermes_constraints_endpoint():
    return (getHost() + ":" + getPort() + ("/psu/v1/constraints"))
# End - def hermes_constraints_endpoint()



# Dummy
def get_dummy_base_url():
    return "http://127.0.0.1:4444"
    

# Avianco (AVI)
def avi_base_url ():
    #return "http://127.0.0.1:4444"
    return "https://app.avianco.io:2002"

def avi_token_endpoint():
    return "https://app.avianco.io:2002/oauth/v1/token"

def avi_refresh_endpoint():
    return "https://app.avianco.io:2002/oauth/v1/token_refresh"

def avi_psu_client_operationalIntents_endpoint (entityid, ovn):
    rval = avi_base_url() + "/psu_client/v1/operational_intent_references" + "/" + entityid
    #rval = avi_base_url() + "/operational_intents/telemetry" + "/" + entityid
    if (not ovn == ""):
        rval = rval + "/" + ovn
    return rval

def avi_psu_client_operationalIntents_telemetry (entityid):
    rval = avi_base_url() + "/psu_client/v1/operational_intents/telemetry" + "/" + entityid
    return rval

def avi_commandUAV_endpoint ():
    rval = avi_base_url() + "/v1/flight/commandUAV"
    return rval


# Frequentis (FCI)
def fci_token_endpoint():
    return "https://fcilabs.net/auth/realms/unt-partners/protocol/openid-connect/token"

def fci_base_url ():
    return "https://fcilabs.net/x4/latest"

def fci_subscription_endpoint ():
    return fci_base_url() + "/coord/v1/subscription"

def fci_constraints_endpoint ():
#    return get_dummy_base_url() + "/psu/v1/constraints" # Development
    return fci_base_url() + "/psu/v1/constraints" # Production

def fci_operationalIntents_endpoint ():
#    return get_dummy_base_url() + "/psu/v1/operational_intents"
    return fci_base_url() + "/psu/v1/operational_intents"

def fci_telemetry_endpoint ():
#    return get_dummy_base_url() + "/coord/v1/vehicle_telemetry" # Development
    return fci_base_url() + "/coord/v1/vehicle_telemetry" # Production


#AAMTEX 
def AAMTEX_token_endpoint():
    return "https://accounts.aamtex.com/auth/tokens"

def AAMTEX_base_url():
    return "https://accounts.aamtex.com"

def DSS_constraint_subscription_endpoint():
    return AAMTEX_base_url() + "/" + "dss/v1/subscriptions"

def AAMTEX_telemetry_endpoint(entityid):
    return AAMTEX_base_url() + "/" + "psu/v1" + "/" "operational_intents" + "/"+ entityid + "/" + "telemetry"


#UNT Endpoint
def UNT_base_url():
    return "http://autonomous-testing1.eng.unt.edu:443"

def UNT_Telemetry():
    return UNT_base_url()+ "/psu/v1/telemetry"


# LoneStar (LST)
def lst_base_url ():
    #return "http://127.0.0.1:4444/psu_client/v1"
    return "https://ls1.tamucc.edu/api/c332/v1/X4"

def lst_psu_client_operationalIntents_endpoint (entityid, ovn):
    rval = lst_base_url() + "/operational_intent_references" + "/" + entityid
    if (not ovn == ""):
        rval = rval + "/" + ovn
    return rval

def lst_telemetry_endpoint ():
    #return get_dummy_base_url() + "/psu/v1/telemetry" # Development
    return lst_base_url() + "/telemetry" # Production


# CASA
def casa_base_url ():
    #return "http://127.0.0.1:4444"
    return "https://emmy8.casa.umass.edu:8046"

def casa_telemetry_endpoint ():
    #return "http://127.0.0.1:4444/psu_client/v1"
    return casa_base_url() + "/telemetry"


# Resilienx
def resilienx_base_url ():
    #return "http://127.0.0.1:4444" 
    return "https://unt.fraihmwork.resilienx.com"

def resilienx_telemetry_url():
    return resilienx_base_url() + "/api/x4/telemetry"

def resilienx_fraihmwork ():
    return resilienx_base_url() + "/api/monitor/v1/component/"

def resilienx_fraihmwork_refresh (refreshID):
    return resilienx_base_url() + "/api/monitor/v1/component" + "/" + refreshID + "/" + "refresh"
