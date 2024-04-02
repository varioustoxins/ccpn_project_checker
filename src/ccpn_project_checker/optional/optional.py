from .nothing import Nothing
from .something import Something


class Optional(object):

    def get(self): ...

    @classmethod
    def of(cls, thing=None, messages=(), error_code=None, cause=None):
        if (thing and messages) or (thing and error_code) or (thing and cause):
            NEWLINE = "\n"
            msg = f"""
            got messages / error / cause  code but thing is not None
            thing 
            -----
            {thing}
            
            messages
            --------
            {NEWLINE.join(messages)}
            
            error code
            ----------
            
            {error_code.value}
            """
            raise Exception(msg)

        result = (
            Something(thing, cls)
            if thing
            else Nothing(cls, messages=messages, error_code=error_code, cause=cause)
        )
        return result

    @classmethod
    def empty(cls, messages=(), error_code=None, cause=None):
        return Nothing(cls, messages=messages, error_code=error_code, cause=cause)
