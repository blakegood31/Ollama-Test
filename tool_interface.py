from abc import ABC, abstractmethod
import subprocess

class Tool(ABC):
    """
    All classes that will be used as a tool in this application must inherit the Tool abstract class.

    Args (Attributes) must be implemented via a method in the subclass. This method must be preceded by the @property decorator and have the same name as the attribute it is associated with.
    Functions must be implemented via a method in the subclass. This method must have the same name as the associated abstract method in the Tool class.


    Implementation details must be provided for the following:

    ## Args (Attributes)
        * `name` - The name of the tool you will be implementing. Tool name should follow Python naming conventions and cannot contain whitespace.
        * `description` - A detailed description of the purpose of the tool, and what types of queries it may be needed for.
        
        Both `name` and `description` use the following format when defined in the subclass (method name matches corresponding attribute)::
            
            @property
            def description(self):
                return "A detailed description of the tool and when to use it"
        
        * `tool_template` - A structured dict that will be passed to Ollama in order to register the tool, following the structure shown::

            @property
            def tool_template(self):
                return {
                    "type": "function",
                    "function": {
                        "name": "tool_name",
                        "description": "Tool description",
                        "parameters": {
                            "type": "object",
                            "required": ["required params (str)"],
                            'properties': {
                                "param1": {
                                    "type": "param type",
                                    "description": "param description"
                                }
                            }
                        }
                    }
                }

    
    ## Methods
    
        `run`: The method that will be called whenever the tool is needed::

            def run(self, args):
                #
                # Code to be executed when the tool is called ...
                #
                tool_data = {"key1": "data"} # Dict containing all data returned by the tool
                return json.dumps(tool_data)

    """
    @abstractmethod
    def run(self) -> str:
        raise NotImplementedError("Needs to implement in subclass")
    
    @property
    @abstractmethod
    def description(self):
        raise NotImplementedError("Must implement the property: 'description'")
    
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError("Must implement the property: 'name'")
    
    @property
    @abstractmethod
    def tool_template(self):
        raise NotImplementedError("Must implement the property: 'name'")