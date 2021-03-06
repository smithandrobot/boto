import os
import urlparse
import boto
import boto.connection
import boto.jsonresponse
import awsqueryrequest

class AWSQueryService(boto.connection.AWSQueryConnection):

    Name = ''
    Description = ''
    APIVersion = ''
    Authentication = 'sign-v2'
    Path = '/'
    Port = 443
    Provider = 'aws'

    Regions = []

    def __init__(self, **args):
        self.args = args
        self.check_for_credential_file()
        self.check_for_euare_url()
        if 'host' not in self.args:
            region_name = self.args.get('region_name', self.Regions[0]['name'])
            for region in self.Regions:
                if region['name'] == region_name:
                    self.args['host'] = region['endpoint']
        if 'path' not in self.args:
            self.args['path'] = self.Path
        if 'port' not in self.args:
            self.args['port'] = self.Port
        boto.connection.AWSQueryConnection.__init__(self, **self.args)
        self.aws_response = None

    def check_for_credential_file(self):
        """
        Checks for the existance of an AWS credential file.
        If the environment variable AWS_CREDENTIAL_FILE is
        set and points to a file, that file will be read and
        will be searched credentials.
        Note that if credentials have been explicitelypassed
        into the class constructor, those values always take
        precedence.
        """
        if 'AWS_CREDENTIAL_FILE' in os.environ:
            path = os.environ['AWS_CREDENTIAL_FILE']
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)
            if os.path.isfile(path):
                fp = open(path)
                lines = fp.readlines()
                fp.close()
                for line in lines:
                    name, value = line.split('=')
                    if name.strip() == 'AWSAccessKeyId':
                        if 'aws_access_key_id' not in self.args:
                            self.args['aws_access_key_id'] = value.strip()
                    elif name.strip() == 'AWSSecretKey':
                        if 'aws_secret_access_key' not in self.args:
                            self.args['aws_secret_access_key'] = value.strip()
            else:
                print 'Warning: unable to read AWS_CREDENTIAL_FILE'

    def check_for_euare_url(self):
        """
        First checks to see if a url argument was explicitly passed
        in.  If so, that will be used.  If not, it checks for the
        existence of the EUARE_URL environment variable.
        If this is set, it should contain a fully qualified URL to the
        service you want to use.
        Note that any values passed explicitly to the class constructor
        will take precedence.
        """
        url = self.args.get('url', None)
        if url:
            del self.args['url']
        # TODO: move EUARE_URL to class variable
        if not url and 'EUARE_URL' in os.environ:
            url = os.environ['EUARE_URL']
        if url:
            rslt = urlparse.urlparse(url)
            if 'is_secure' not in self.args:
                if rslt.scheme == 'https':
                    self.args['is_secure'] = True
                else:
                    self.args['is_secure'] = False

            host = rslt.netloc
            port = None
            l = host.split(':')
            if len(l) > 1:
                host = l[0]
                port = int(l[1])
            if 'host' not in self.args:
                self.args['host'] = host
            if port and 'port' not in self.args:
                self.args['port'] = port

            if rslt.path and 'path' not in self.args:
                self.args['path'] = rslt.path
            
    def _required_auth_capability(self):
        return [self.Authentication]
        
