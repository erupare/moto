import boto
from boto.exception import S3ResponseError
from boto.s3.key import Key
import requests

import sure

from moto import mock_s3


class MyModel(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def save(self):
        conn = boto.connect_s3('the_key', 'the_secret')
        bucket = conn.get_bucket('mybucket')
        k = Key(bucket)
        k.key = self.name
        k.set_contents_from_string(self.value)


@mock_s3
def test_my_model_save():
    # Create Bucket so that test can run
    conn = boto.connect_s3('the_key', 'the_secret')
    conn.create_bucket('mybucket')
    ####################################

    model_instance = MyModel('steve', 'is awesome')
    model_instance.save()

    assert conn.get_bucket('mybucket').get_key('steve').get_contents_as_string() == 'is awesome'


@mock_s3
def test_missing_key():
    conn = boto.connect_s3('the_key', 'the_secret')
    bucket = conn.create_bucket("foobar")
    bucket.get_key("the-key").should.equal(None)


@mock_s3
def test_copy_key():
    conn = boto.connect_s3('the_key', 'the_secret')
    bucket = conn.create_bucket("foobar")
    key = Key(bucket)
    key.key = "the-key"
    key.set_contents_from_string("some value")

    bucket.copy_key('new-key', 'foobar', 'the-key')

    bucket.get_key("the-key").get_contents_as_string().should.equal("some value")
    bucket.get_key("new-key").get_contents_as_string().should.equal("some value")


@mock_s3
def test_missing_bucket():
    conn = boto.connect_s3('the_key', 'the_secret')
    conn.get_bucket.when.called_with('mybucket').should.throw(S3ResponseError)


@mock_s3
def test_bucket_deletion():
    conn = boto.connect_s3('the_key', 'the_secret')
    bucket = conn.create_bucket("foobar")

    key = Key(bucket)
    key.key = "the-key"
    key.set_contents_from_string("some value")

    # Try to delete a bucket that still has keys
    conn.delete_bucket.when.called_with("foobar").should.throw(S3ResponseError)

    bucket.delete_key("the-key")
    conn.delete_bucket("foobar")

    # Get non-existing bucket
    conn.get_bucket.when.called_with("foobar").should.throw(S3ResponseError)

    # Delete non-existant bucket
    conn.delete_bucket.when.called_with("foobar").should.throw(S3ResponseError)


@mock_s3
def test_get_all_buckets():
    conn = boto.connect_s3('the_key', 'the_secret')
    bucket = conn.create_bucket("foobar")
    bucket = conn.create_bucket("foobar2")
    buckets = conn.get_all_buckets()

    buckets.should.have.length_of(2)


@mock_s3
def test_bucket_method_not_implemented():
    requests.post.when.called_with("https://foobar.s3.amazonaws.com/").should.throw(NotImplementedError)


@mock_s3
def test_key_method_not_implemented():
    requests.post.when.called_with("https://foobar.s3.amazonaws.com/foo").should.throw(NotImplementedError)
