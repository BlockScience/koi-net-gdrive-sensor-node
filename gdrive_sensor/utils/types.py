from rid_lib.core import ORN, RID
folderType = 'application/vnd.google-apps.folder'
docsType = 'application/vnd.google-apps.document'
sheetsType = 'application/vnd.google-apps.spreadsheet'
presentationType = 'application/vnd.google-apps.presentation'
photoType = 'application/vnd.google-apps.photo'

# ToDo: Separate GoogleDriveFile, the Spec. File type (distinguash between files and folder outside of Type)

class GoogleWorkspace(ORN):
    namespace = 'google.workspace'
    url = 'https://drive.google.com'

    def __init__(self, id: str):
        self.id = id

    @property
    def https_rid_obj(self):
        return RID.from_string(self.url)

    @property
    def reference(self):
        return self.id

    @classmethod
    def from_reference(cls, id):
        if len(id) >= 1:
            return cls(id)
        return None

class GoogleWorkspaceDoc(GoogleWorkspace):
    @property
    def url(self):
        return f'https://drive.google.com/file/d/{self.id}'

class GoogleDriveFolder(GoogleWorkspace):
    namespace = f'google_drive.folder'

    @property
    def url(self):
        return f'https://drive.google.com/drive/folders/{self.id}'


class GoogleDriveFile(GoogleWorkspaceDoc):
    namespace = f'google_drive.file'

class GoogleDoc(GoogleDriveFile):
    namespace = f'google_docs.document'

class GoogleSheets(GoogleDriveFile):
    namespace = f'google_sheets.spreadsheet'

class GoogleSlides(GoogleDriveFile):
    namespace = f'google_slides.presentation'

class GoogleWorkspaceApp(GoogleWorkspace):
    namespace = f'google.workspace'

    def __init__(self, id: str):
        self.id = id
        self.mime_type = None
        self.google_rid = None
        self.https_rid = None

    def google_object(self, mime_type):
        self.mime_type = mime_type
        mime_types = [folderType, docsType, sheetsType, presentationType]
        if self.mime_type == folderType:
            self.google_rid = GoogleDriveFolder.from_reference(self.id)
            self.namespace = f'{self.namespace}.{GoogleDriveFolder.namespace}'
        elif self.mime_type == docsType:
            self.google_rid = GoogleDoc.from_reference(self.id)
            self.namespace = f'{self.namespace}.{GoogleDoc.namespace}'
        elif self.mime_type == sheetsType:
            self.google_rid = GoogleSheets.from_reference(self.id)
            self.namespace = f'{self.namespace}.{GoogleSheets.namespace}'
        elif self.mime_type == presentationType:
            self.google_rid = GoogleSlides.from_reference(self.id)
            self.namespace = f'{self.namespace}.{GoogleSlides.namespace}'
        elif self.mime_type not in mime_types:
            self.google_rid = GoogleDriveFile.from_reference(self.id)
            self.namespace = f'{self.namespace}.{GoogleDriveFile.namespace}'
        self.https_rid = self.google_rid.https_rid_obj
        return self.google_rid