import logging

logger = logging.getLogger("Inochi2D-Parameters")

class ParameterController:
    def __init__(self):
        self.default_parameters = {
            "HeadX": 0.0,
            "HeadY": 0.0,
            "HeadZ": 0.0,
            "EyeOpen": 1.0,
            "MouthOpen": 0.0,
        }

    def apply_params(self, puppet, params_dict):
        """
        Updates the puppet rig parameters.
        params_dict: dict with parameter names and values (usually -1.0 to 1.0)
        """
        if isinstance(puppet, str): # Mock puppet
            return

        # Attempt to find the parameter setting method
        # Common patterns: puppet.find_parameter(name).value = val
        # or puppet.set_parameter(name, val)

        find_param = getattr(puppet, 'find_parameter', None) or getattr(puppet, 'get_parameter', None)
        set_param_direct = (
            getattr(puppet, 'set_parameter', None) or
            getattr(puppet, 'set_param', None) or
            getattr(puppet, 'set_parameter_value', None)
        )

        for name, value in params_dict.items():
            try:
                if set_param_direct:
                    set_param_direct(name, value)
                    logger.debug(f"Set parameter {name} to {value} via direct method")
                elif find_param:
                    param = find_param(name)
                    if param:
                        # Try setting value property or via method
                        if hasattr(param, 'value'):
                            param.value = value
                            logger.debug(f"Set parameter {name} to {value} via property")
                        elif hasattr(param, 'set_value'):
                            param.set_value(value)
                            logger.debug(f"Set parameter {name} to {value} via method")
                        else:
                            logger.warning(f"Parameter {name} found but has no settable value attribute.")
                    else:
                        logger.warning(f"Parameter {name} not found in puppet rig.")
                else:
                    logger.warning("Puppet object provides no method to set parameters.")
                    break
            except Exception as e:
                logger.error(f"Error setting parameter {name}: {e}")

    def map_normalized_value(self, value, param_range=(-1.0, 1.0)):
        min_val, max_val = param_range
        return min_val + (max_val - min_val) * value
