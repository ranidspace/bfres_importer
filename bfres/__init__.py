if "bpy" in locals():
    import importlib
    names = ('BinaryStruct', 'FRES', 'FMDL', 'Importer', 'Exporter',
    'YAZ0')
    for name in names:
        ls = locals()
        if name in ls:
            importlib.reload(ls[name])