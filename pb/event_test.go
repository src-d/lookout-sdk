package pb

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestParseRepositoryInfo(t *testing.T) {
	require := require.New(t)

	successCases := []struct {
		Input    string
		Expected RepositoryInfo
	}{
		{
			Input: "github.com/foo/bar",
			Expected: RepositoryInfo{
				CloneURL: "https://github.com/foo/bar",
				Host:     "github.com",
				FullName: "foo/bar",
				Owner:    "foo",
				Name:     "bar",
			},
		},
		{
			Input: "https://github.com/foo/bar",
			Expected: RepositoryInfo{
				CloneURL: "https://github.com/foo/bar",
				Host:     "github.com",
				FullName: "foo/bar",
				Owner:    "foo",
				Name:     "bar",
			},
		},
		{
			Input: "https://token@github.com/foo/bar",
			Expected: RepositoryInfo{
				CloneURL: "https://token@github.com/foo/bar",
				Host:     "github.com",
				FullName: "foo/bar",
				Owner:    "foo",
				Name:     "bar",
			},
		},
		{
			Input: "gitlab.com/foo/bar",
			Expected: RepositoryInfo{
				CloneURL: "https://gitlab.com/foo/bar",
				Host:     "gitlab.com",
				FullName: "foo/bar",
				Owner:    "foo",
				Name:     "bar",
			},
		},
		{
			Input: "bitbucket.org/foo/bar",
			Expected: RepositoryInfo{
				CloneURL: "https://bitbucket.org/foo/bar",
				Host:     "bitbucket.org",
				FullName: "foo/bar",
				Owner:    "foo",
				Name:     "bar",
			},
		},
	}

	errorCases := []struct {
		Input    string
		Expected string
	}{
		{
			Input:    "",
			Expected: "host can't be empty",
		},
		{
			Input:    "\n",
			Expected: "parse https://\n: invalid character \"\\n\" in host name",
		},
		{
			Input:    "http://github.com/foo/bar",
			Expected: "only https urls are supported",
		},
		{
			Input:    "git://github.com:foo/bar",
			Expected: "only https urls are supported",
		},
		{
			Input:    "foo/bar",
			Expected: "host foo is not supported",
		},
		{
			Input:    "github.com/foo",
			Expected: "unsupported path foo",
		},
		{
			Input:    "github.com/foo/bar/rest",
			Expected: "unsupported path foo/bar/rest",
		},
	}

	for _, c := range successCases {
		actual, err := ParseRepositoryInfo(c.Input)
		require.NoError(err)
		require.Equal(actual, &c.Expected)
	}

	for _, c := range errorCases {
		actual, err := ParseRepositoryInfo(c.Input)
		require.EqualError(err, c.Expected)
		require.Nil(actual)
	}
}
