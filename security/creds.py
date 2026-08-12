import ctypes
import os
from ctypes import wintypes

TARGET = "ocr_app_baidu_ocr"

CRED_TYPE_GENERIC = 1
CRED_PERSIST_LOCAL_MACHINE = 2
CRED_MAX_CREDENTIAL_BLOB_SIZE = 512


class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


_advapi = ctypes.windll.advapi32
_advapi.CredWriteW.argtypes = [ctypes.POINTER(CREDENTIAL), wintypes.DWORD]
_advapi.CredWriteW.restype = wintypes.BOOL
_advapi.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                              ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
_advapi.CredReadW.restype = wintypes.BOOL
_advapi.CredFree.argtypes = [ctypes.c_void_p]
_advapi.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
_advapi.CredDeleteW.restype = wintypes.BOOL


def save_baidu_creds(api_key: str, secret_key: str) -> None:
    blob = f"{api_key}\n{secret_key}".encode("utf-8")
    if len(blob) > CRED_MAX_CREDENTIAL_BLOB_SIZE:
        raise ValueError("credential blob too large")
    buffer = ctypes.create_string_buffer(blob)
    cred = CREDENTIAL()
    cred.Type = CRED_TYPE_GENERIC
    cred.TargetName = TARGET
    cred.CredentialBlobSize = len(blob)
    cred.CredentialBlob = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))
    cred.Persist = CRED_PERSIST_LOCAL_MACHINE
    cred.UserName = "ocr_app"
    if not _advapi.CredWriteW(ctypes.byref(cred), 0):
        raise OSError(ctypes.get_last_error(), "CredWriteW failed")


def get_baidu_creds() -> tuple[str, str] | None:
    pcred = ctypes.POINTER(CREDENTIAL)()
    if not _advapi.CredReadW(TARGET, CRED_TYPE_GENERIC, 0, ctypes.byref(pcred)):
        return None
    try:
        cred = pcred.contents
        blob = ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize).decode("utf-8")
        api_key, _, secret_key = blob.partition("\n")
        return api_key, secret_key
    finally:
        _advapi.CredFree(pcred)


def delete_baidu_creds() -> None:
    _advapi.CredDeleteW(TARGET, CRED_TYPE_GENERIC, 0)
