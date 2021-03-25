import importlib


class DynamicImport:
    """Class for dynamic import modules and instances objects of target class"""

    @staticmethod
    def get_object(logger, mod_name, target_cls, base_cls: type = None,
                   **kwargs):
        """
        Imports the module, searches target class in the module,
        verifies that target class is a subclass of base class

        :param logger: logger object
        :param mod_name: module name to import
        :param target_cls: target class name
        :param base_cls: base class name
        :param kwargs: parameters to created object of target class
        :return: object of target class, which was created with kwargs

        """
        module = importlib.import_module(mod_name)
        assert hasattr(module, target_cls), \
            "class {} is not in {}".format(target_cls, mod_name)
        logger.debug('reading class {} from module {}'.format(target_cls,
                                                              mod_name))
        cls = getattr(module, target_cls)
        if base_cls:
            assert issubclass(cls, base_cls), \
                "class {} should inherit from {}".format(target_cls,
                                                         base_cls.__name__)
        logger.debug('initialising {} with params {}'.format(target_cls,
                                                             kwargs))
        return cls(**kwargs)
