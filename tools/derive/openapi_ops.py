"""C-number -> request/response binding for the OpenAPI documents.

Appendix C fixes the method, path, purpose, permission and per-endpoint notes
of all 107 operations. It does not tabulate bodies, so this table binds each
operation to a representation from openapi_schemas.py. Every binding is
traceable to the card's Purpose line plus the Appendix A table that owns the
resource; nothing here contradicts a card.

Keys:
  doc       which of the four Master §0.3 documents the operation belongs to
  req       request body schema name, or None
  res       response body schema name, or None (204)
  status    success status code (default 200, or 201/202/204 where the card says so)
  list      response is a cursor page of `res`
  binary    response is a stream, not JSON
  op        operationId; derived once, here, so it is stable across regeneration
"""

PUBLIC = "public-control"
MAILBOX = "mailbox"
PROVISIONING = "internal-provisioning"
OPERATIONS = "operations"

OPS = {
    # --- organisation -----------------------------------------------------
    "C.1": dict(doc=PUBLIC, op="getOrganisationMailProfile", res="OrganisationMailProfile"),
    "C.2": dict(doc=PUBLIC, op="updateOrganisationMailProfile", req="OrganisationMailProfileUpdate", res="OrganisationMailProfile"),
    "C.3": dict(doc=PUBLIC, op="getOrganisationEntitlements", res="EntitlementSnapshot"),
    "C.4": dict(doc=PUBLIC, op="listOrganisationMembers", res="Member", list=True),
    "C.5": dict(doc=PUBLIC, op="replaceMemberRoles", req="MemberRolesReplacement", res="Member"),
    # --- domains ----------------------------------------------------------
    "C.6": dict(doc=PUBLIC, op="listOrganisationDomains", res="Domain", list=True),
    "C.7": dict(doc=PUBLIC, op="createDomain", req="DomainCreateRequest", res="Domain", status=201),
    "C.8": dict(doc=PUBLIC, op="getDomain", res="Domain"),
    "C.9": dict(doc=PUBLIC, op="updateDomain", req="DomainUpdate", res="Domain"),
    "C.10": dict(doc=PUBLIC, op="deleteDomain", res="Domain", status=202),
    "C.11": dict(doc=PUBLIC, op="renewDomainVerification", res="DomainVerificationChallenge", status=201),
    "C.12": dict(doc=PUBLIC, op="checkDomainVerification", res="DomainVerificationChallenge", status=202),
    "C.13": dict(doc=PUBLIC, op="getDomainDnsStatus", res="DomainDnsStatus"),
    "C.14": dict(doc=PUBLIC, op="checkDomainDns", res="ProvisioningOperation", status=202),
    "C.15": dict(doc=PUBLIC, op="activateDomain", res="Domain", status=202),
    "C.16": dict(doc=PUBLIC, op="suspendDomain", req="ReasonRequest", res="Domain"),
    "C.17": dict(doc=PUBLIC, op="restoreDomain", res="Domain", status=202),
    "C.18": dict(doc=PUBLIC, op="getDomainDkim", res="DkimState"),
    "C.19": dict(doc=PUBLIC, op="rotateDomainDkim", req="DkimRotateRequest", res="DkimState", status=202),
    "C.20": dict(doc=PUBLIC, op="requestDomainTransfer", req="DomainTransferRequest", res="DomainTransfer", status=201),
    "C.21": dict(doc=PUBLIC, op="getDomainTransfer", res="DomainTransfer"),
    "C.22": dict(doc=PUBLIC, op="approveDomainTransfer", res="DomainTransfer", status=202),
    "C.23": dict(doc=PUBLIC, op="cancelDomainTransfer", res="DomainTransfer"),
    # --- mailboxes --------------------------------------------------------
    "C.24": dict(doc=PUBLIC, op="listOrganisationMailboxes", res="Mailbox", list=True),
    "C.25": dict(doc=PUBLIC, op="createMailbox", req="MailboxCreateRequest", res="Mailbox", status=201),
    "C.26": dict(doc=PUBLIC, op="getMailbox", res="Mailbox"),
    "C.27": dict(doc=PUBLIC, op="updateMailbox", req="MailboxUpdate", res="Mailbox"),
    "C.28": dict(doc=PUBLIC, op="updateMailboxQuota", req="MailboxQuotaUpdate", res="Mailbox", status=202),
    "C.29": dict(doc=PUBLIC, op="suspendMailbox", req="ReasonRequest", res="Mailbox"),
    "C.30": dict(doc=PUBLIC, op="restoreMailbox", res="Mailbox", status=202),
    "C.31": dict(doc=PUBLIC, op="deleteMailbox", res="Mailbox", status=202),
    "C.32": dict(doc=PUBLIC, op="recoverMailbox", res="Mailbox", status=202),
    "C.33": dict(doc=PUBLIC, op="getMailboxUsage", res="MailboxUsage"),
    "C.34": dict(doc=PUBLIC, op="listMailboxAccessGrants", res="MailboxAccessGrant", list=True),
    "C.35": dict(doc=PUBLIC, op="createMailboxAccessGrant", req="MailboxAccessGrantRequest", res="MailboxAccessGrant", status=201),
    "C.36": dict(doc=PUBLIC, op="deleteMailboxAccessGrant", status=204),
    # --- aliases and identities ------------------------------------------
    "C.37": dict(doc=PUBLIC, op="listDomainAliases", res="Alias", list=True),
    "C.38": dict(doc=PUBLIC, op="createAlias", req="AliasWrite", res="Alias", status=201),
    "C.39": dict(doc=PUBLIC, op="getAlias", res="Alias"),
    "C.40": dict(doc=PUBLIC, op="replaceAlias", req="AliasWrite", res="Alias"),
    "C.41": dict(doc=PUBLIC, op="deleteAlias", status=204),
    "C.42": dict(doc=PUBLIC, op="listMailboxIdentities", res="MailboxIdentity", list=True),
    "C.43": dict(doc=PUBLIC, op="createMailboxIdentity", req="MailboxIdentityCreate", res="MailboxIdentity", status=201),
    "C.44": dict(doc=PUBLIC, op="updateMailboxIdentity", req="MailboxIdentityUpdate", res="MailboxIdentity"),
    "C.45": dict(doc=PUBLIC, op="deleteMailboxIdentity", status=204),
    # --- groups -----------------------------------------------------------
    "C.46": dict(doc=PUBLIC, op="listDomainGroups", res="DistributionGroup", list=True),
    "C.47": dict(doc=PUBLIC, op="createDistributionGroup", req="DistributionGroupWrite", res="DistributionGroup", status=201),
    "C.48": dict(doc=PUBLIC, op="getDistributionGroup", res="DistributionGroup"),
    "C.49": dict(doc=PUBLIC, op="updateDistributionGroup", req="DistributionGroupWrite", res="DistributionGroup"),
    "C.50": dict(doc=PUBLIC, op="deleteDistributionGroup", status=204),
    "C.51": dict(doc=PUBLIC, op="listGroupMembers", res="GroupMember", list=True),
    "C.52": dict(doc=PUBLIC, op="addGroupMember", req="GroupMemberCreate", res="GroupMember", status=201),
    "C.53": dict(doc=PUBLIC, op="removeGroupMember", status=204),
    # --- mailbox settings -------------------------------------------------
    "C.54": dict(doc=PUBLIC, op="getMailboxForwarding", res="ForwardingRule"),
    "C.55": dict(doc=PUBLIC, op="replaceMailboxForwarding", req="ForwardingRuleWrite", res="ForwardingRule"),
    "C.56": dict(doc=PUBLIC, op="getMailboxVacation", res="VacationRule"),
    "C.57": dict(doc=PUBLIC, op="replaceMailboxVacation", req="VacationRuleWrite", res="VacationRule"),
    "C.58": dict(doc=PUBLIC, op="getMailboxFilters", res="FilterSet"),
    "C.59": dict(doc=PUBLIC, op="replaceMailboxFilters", req="FilterSetWrite", res="FilterSet", status=202),
    "C.60": dict(doc=PUBLIC, op="validateMailboxFilters", req="FilterSetWrite", res="FilterValidationResult"),
    # --- sessions and credentials ----------------------------------------
    "C.61": dict(doc=PUBLIC, op="listMyMailSessions", res="MailSession", list=True),
    "C.62": dict(doc=PUBLIC, op="revokeMyMailSession", res="MailSession"),
    "C.63": dict(doc=PUBLIC, op="listMailboxAppPasswords", res="AppPassword", list=True),
    "C.64": dict(doc=PUBLIC, op="createMailboxAppPassword", req="AppPasswordCreateRequest", res="AppPasswordCreated", status=201),
    "C.65": dict(doc=PUBLIC, op="deleteMailboxAppPassword", status=204),
    # --- mailbox data plane ----------------------------------------------
    "C.66": dict(doc=MAILBOX, op="listFolders", res="Folder", list=True),
    "C.67": dict(doc=MAILBOX, op="createFolder", req="FolderCreate", res="Folder", status=201),
    "C.68": dict(doc=MAILBOX, op="updateFolder", req="FolderUpdate", res="Folder"),
    "C.69": dict(doc=MAILBOX, op="deleteFolder", status=204),
    "C.70": dict(doc=MAILBOX, op="listMessages", res="MessageSummary", list=True),
    "C.71": dict(doc=MAILBOX, op="getMessage", res="MessageView"),
    "C.72": dict(doc=MAILBOX, op="getMessageContent", res="MessageContent"),
    "C.73": dict(doc=MAILBOX, op="getMessageRaw", binary=True, media="message/rfc822"),
    "C.74": dict(doc=MAILBOX, op="getMessageAttachment", binary=True, media="application/octet-stream"),
    "C.75": dict(doc=MAILBOX, op="mutateMessageFlags", req="FlagMutationRequest", res="BulkMutationResult"),
    "C.76": dict(doc=MAILBOX, op="moveMessages", req="MessageTransferRequest", res="BulkMutationResult"),
    "C.77": dict(doc=MAILBOX, op="copyMessages", req="MessageTransferRequest", res="BulkMutationResult"),
    "C.78": dict(doc=MAILBOX, op="trashMessages", req="MessageRefBatch", res="BulkMutationResult"),
    "C.79": dict(doc=MAILBOX, op="expungeMessages", req="ExpungeRequest", res="BulkMutationResult"),
    "C.80": dict(doc=MAILBOX, op="getThread", res="Thread"),
    "C.81": dict(doc=MAILBOX, op="searchMessages", res="SearchResult"),
    "C.82": dict(doc=MAILBOX, op="listDrafts", res="Draft", list=True),
    "C.83": dict(doc=MAILBOX, op="createDraft", req="DraftWrite", res="Draft", status=201),
    "C.84": dict(doc=MAILBOX, op="getDraft", res="Draft"),
    "C.85": dict(doc=MAILBOX, op="replaceDraft", req="DraftWrite", res="Draft"),
    "C.86": dict(doc=MAILBOX, op="deleteDraft", status=204),
    "C.87": dict(doc=MAILBOX, op="stageComposeAttachment", req_media="multipart/form-data", res="StagedAttachment", status=201),
    "C.88": dict(doc=MAILBOX, op="getComposeAttachment", binary=True, media="application/octet-stream"),
    "C.89": dict(doc=MAILBOX, op="deleteComposeAttachment", status=204),
    "C.90": dict(doc=MAILBOX, op="sendMessage", req="SendRequest", res="SubmissionRecord", status=202),
    "C.91": dict(doc=MAILBOX, op="getSubmission", res="SubmissionRecord"),
    # --- audit, security, exports, restrictions --------------------------
    "C.92": dict(doc=PUBLIC, op="listAuditEvents", res="AuditEvent", list=True),
    "C.93": dict(doc=PUBLIC, op="listSecurityEvents", res="SecurityEvent", list=True),
    "C.94": dict(doc=PUBLIC, op="createDataExport", req="DataExportRequest", res="DataExportJob", status=202),
    "C.95": dict(doc=PUBLIC, op="getDataExport", res="DataExportJob"),
    "C.96": dict(doc=PUBLIC, op="listMailboxRestrictions", res="Restriction", list=True),
    # --- internal provisioning -------------------------------------------
    "C.97": dict(doc=PROVISIONING, op="reportResourceObservation", req="ObservationReport", res="ObservationAccepted"),
    "C.98": dict(doc=PROVISIONING, op="getResourceDesiredState", res="DesiredState"),
    "C.99": dict(doc=PROVISIONING, op="reportProvisioningStarted", req="ProvisioningStarted", res="ProvisioningOperation"),
    "C.100": dict(doc=PROVISIONING, op="reportProvisioningResult", req="ProvisioningResult", res="ProvisioningOperation"),
    "C.105": dict(doc=PROVISIONING, op="getLiveness", res="HealthStatus", unauthenticated=True),
    "C.106": dict(doc=PROVISIONING, op="getReadiness", res="HealthStatus", unauthenticated=True),
    "C.107": dict(doc=PROVISIONING, op="getVersion", res="VersionInfo"),
    # --- operations -------------------------------------------------------
    "C.101": dict(doc=OPERATIONS, op="requestRestriction", req="RestrictionRequest", res="Restriction", status=202),
    "C.102": dict(doc=OPERATIONS, op="clearRestriction", res="Restriction"),
    "C.103": dict(doc=OPERATIONS, op="getResourceDiagnostics", res="ResourceDiagnostics"),
    "C.104": dict(doc=OPERATIONS, op="submitSecurityEvent", req="SecurityEventSubmission", status=202, res="SecurityEventAccepted"),
}

# Query parameters that a card's Notes name explicitly. Nothing is added that a
# card does not mention: an invented filter is an invented contract.
QUERY = {
    "C.4": ["cursor", "limit"],
    "C.6": ["cursor", "limit", "state", "q"],
    "C.24": ["cursor", "limit", "domain_id", "state", "q"],
    "C.37": ["cursor", "limit"],
    "C.46": ["cursor", "limit"],
    "C.51": ["cursor", "limit"],
    "C.34": ["cursor", "limit"],
    "C.42": ["cursor", "limit"],
    "C.61": ["cursor", "limit"],
    "C.63": ["cursor", "limit"],
    "C.66": [],
    "C.70": ["folder_ref", "cursor", "limit"],
    "C.81": ["q", "folder_ref", "cursor", "limit"],
    "C.82": ["cursor", "limit"],
    "C.92": ["cursor", "limit", "from", "to", "action", "resource_type"],
    "C.93": ["cursor", "limit", "from", "to", "severity"],
    "C.96": ["cursor", "limit"],
}
