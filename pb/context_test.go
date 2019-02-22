package pb

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
)

type ContextTestSuite struct {
	suite.Suite
	ctxEmpty         context.Context
	ctxNoLogFields   context.Context
	ctxWithLogFields context.Context
}

func TestContextTestSuite(t *testing.T) {
	suite.Run(t, new(ContextTestSuite))
}

func (s *ContextTestSuite) SetupSuite() {
	s.ctxEmpty = context.Background()
	s.ctxNoLogFields = context.WithValue(
		context.Background(), logFieldsKeyContext, Fields{})
	s.ctxWithLogFields = context.WithValue(
		context.Background(), logFieldsKeyContext, Fields{
			"a": 1,
			"b": 2,
			"c": 3,
		})
}

func (s *ContextTestSuite) ensureInitialCtxEmptyUnchanged(require *require.Assertions) {
	s.T().Helper()

	require.Nil(s.ctxEmpty.Value(logFieldsKeyContext))
}

func (s *ContextTestSuite) ensureInitialCtxNoLogFieldsUnchanged(require *require.Assertions) {
	s.T().Helper()

	fields := s.ctxNoLogFields.Value(logFieldsKeyContext).(Fields)
	require.NotNil(fields)
	require.Equal(0, len(fields))
}

func (s *ContextTestSuite) ensureInitialCtxWithLogFieldsUnchanged(require *require.Assertions) {
	s.T().Helper()

	fields := s.ctxWithLogFields.Value(logFieldsKeyContext).(Fields)
	require.NotNil(fields)
	require.Equal(3, len(fields))
	require.Equal(1, fields["a"])
	require.Equal(2, fields["b"])
	require.Equal(3, fields["c"])
}

func (s *ContextTestSuite) TestGet() {
	s.T().Run("empty context", func(t *testing.T) {
		s.ensureInitialCtxEmptyUnchanged(require.New(t))
	})

	s.T().Run("context with no log fields", func(t *testing.T) {
		s.ensureInitialCtxNoLogFieldsUnchanged(require.New(t))
	})

	s.T().Run("empty context", func(t *testing.T) {
		s.ensureInitialCtxWithLogFieldsUnchanged(require.New(t))
	})
}

func (s *ContextTestSuite) TestAdd() {
	s.T().Run("empty context", func(t *testing.T) {
		require := require.New(t)

		fields := GetLogFields(AddLogFields(
			s.ctxEmpty, Fields{"a": 4, "d": 5}))

		require.NotNil(fields)
		require.Equal(2, len(fields))
		require.Equal(4, fields["a"])
		require.Equal(5, fields["d"])

		s.ensureInitialCtxEmptyUnchanged(require)
	})

	s.T().Run("context without log fields", func(t *testing.T) {
		require := require.New(t)

		fields := GetLogFields(AddLogFields(
			s.ctxNoLogFields, Fields{"a": 4, "d": 5}))

		require.NotNil(fields)
		require.Equal(2, len(fields))
		require.Equal(4, fields["a"])
		require.Equal(5, fields["d"])

		s.ensureInitialCtxNoLogFieldsUnchanged(require)
	})

	s.T().Run("context with log fields", func(t *testing.T) {
		require := require.New(t)

		fields := GetLogFields(AddLogFields(
			s.ctxWithLogFields, Fields{"a": 4, "d": 5}))

		require.NotNil(fields)
		require.Equal(4, len(fields))
		require.Equal(1, fields["a"])
		require.Equal(2, fields["b"])
		require.Equal(3, fields["c"])
		require.Equal(5, fields["d"])

		s.ensureInitialCtxWithLogFieldsUnchanged(require)
	})
}
