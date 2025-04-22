from rid_lib.core import ORN, RID
folderType = 'application/vnd.google-apps.folder'
docsType = 'application/vnd.google-apps.document'
sheetsType = 'application/vnd.google-apps.spreadsheet'
presentationType = 'application/vnd.google-apps.presentation'
photoType = 'application/vnd.google-apps.photo'

class GoogleItem(ORN):
    namespace = 'google'

    def __init__(self, id: str):
        self.id = id

    @property
    def reference(self):
        return self.id

    @classmethod
    def from_reference(cls, id):
        if len(id) >= 1:
            return cls(id)
        return None

class GoogleFolder(GoogleItem):
    namespace = f'{GoogleItem.namespace}_drive.folder'

    @property
    def url(self):
        return f'https://drive.google.com/drive/folders/{self.id}'

    @property
    def https_rid_obj(self):
        return RID.from_string(self.url)

class GoogleFile(GoogleItem):
    namespace = f'{GoogleItem.namespace}_drive.file'

    @property
    def url(self):
        return f'https://drive.google.com/file/d/{self.id}'

    @property
    def https_rid_obj(self):
        return RID.from_string(self.url)

class GoogleDoc(GoogleFile):
    namespace = f'{GoogleItem.namespace}_docs.document'

class GoogleSheets(GoogleFile):
    namespace = f'{GoogleItem.namespace}_sheets.spreadsheet'

class GooglePresentation(GoogleFile):
    namespace = f'{GoogleItem.namespace}_slides.presentation'

class GoogleDrive(GoogleItem):
    namespace = f'{GoogleItem.namespace}_drive'

    def __init__(self, id: str):
        self.id = id
        self.mime_type = None
        self.google_rid_obj = None
        self.https_rid_obj = None

    def google_object(self, mime_type):
        self.mime_type = mime_type
        mime_types = [folderType, docsType, sheetsType, presentationType]
        if self.mime_type == folderType:
            self.google_rid_obj = GoogleFolder.from_reference(self.id)
        elif self.mime_type == docsType:
            self.google_rid_obj = GoogleDoc.from_reference(self.id)
        elif self.mime_type == sheetsType:
            self.google_rid_obj = GoogleSheets.from_reference(self.id)
        elif self.mime_type == presentationType:
            self.google_rid_obj = GooglePresentation.from_reference(self.id)
        elif self.mime_type not in mime_types:
            self.google_rid_obj = GoogleFile.from_reference(self.id)
        self.https_rid_obj = self.google_rid_obj.https_rid_obj
        return self.google_rid_obj