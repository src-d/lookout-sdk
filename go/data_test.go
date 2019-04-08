package sdk

import (
	"context"
	"fmt"
	"net"
	"testing"

	"github.com/stretchr/testify/require"
	"google.golang.org/grpc"
	"gopkg.in/src-d/lookout-sdk.v0/pb"
)

var changes []*Change
var files []*File

func init() {
	size := 3
	for i := 0; i < size; i++ {
		changes = append(changes, &Change{
			Head: &File{
				Path: fmt.Sprintf("myfile%d", i),
			},
		})
	}

	for i := 0; i < size; i++ {
		files = append(files, &File{
			Path: fmt.Sprintf("myfile%d", i),
		})
	}
}

func setupDataServer(t *testing.T, srv pb.DataServer) (*grpc.Server, *DataClient) {
	t.Helper()
	require := require.New(t)

	grpcServer := grpc.NewServer()
	pb.RegisterDataServer(grpcServer, srv)

	lis, err := net.Listen("tcp", "localhost:0")
	require.NoError(err)
	address := lis.Addr().String()

	go grpcServer.Serve(lis)

	conn, err := grpc.Dial(address, grpc.WithInsecure())
	require.NoError(err)

	client := NewDataClient(conn)

	return grpcServer, client
}

func TestDataClientGetChanges(t *testing.T) {
	require := require.New(t)

	req := &ChangesRequest{
		Head: &pb.ReferencePointer{
			InternalRepositoryURL: "repo",
			Hash:                  "5262fd2b59d10e335a5c941140df16950958322d",
		},
	}
	_, c := setupDataServer(t, &mockDataServer{
		t:          t,
		changesReq: req,
		changes:    changes,
	})

	s, err := c.GetChanges(context.TODO(), req)
	require.NoError(err)

	var scannedChanges []*Change
	for s.Next() {
		scannedChanges = append(scannedChanges, s.Change())
	}

	require.False(s.Next())
	require.NoError(s.Err())
	require.NoError(s.Close())

	require.Len(scannedChanges, 3)
}

func TestDataClientGetFiles(t *testing.T) {
	require := require.New(t)

	req := &FilesRequest{
		Revision: &pb.ReferencePointer{
			InternalRepositoryURL: "repo",
			Hash:                  "5262fd2b59d10e335a5c941140df16950958322d",
		},
	}
	_, c := setupDataServer(t, &mockDataServer{
		t:        t,
		filesReq: req,
		files:    files,
	})

	s, err := c.GetFiles(context.TODO(), req)
	require.NoError(err)

	var scannedFiles []*File
	for s.Next() {
		scannedFiles = append(scannedFiles, s.File())
	}

	require.False(s.Next())
	require.NoError(s.Err())
	require.NoError(s.Close())

	require.Len(scannedFiles, 3)
}

// Implements DataServer interface
type mockDataServer struct {
	t *testing.T

	changesReq *ChangesRequest
	changes    []*Change

	filesReq *FilesRequest
	files    []*File
}

func (s *mockDataServer) GetChanges(req *ChangesRequest, srv pb.Data_GetChangesServer) (err error) {
	require := require.New(s.t)
	require.Equal(s.changesReq, req)

	for _, c := range s.changes {
		if err := srv.Send(c); err != nil {
			return err
		}
	}

	return nil
}

func (s *mockDataServer) GetFiles(req *FilesRequest, srv pb.Data_GetFilesServer) error {
	require := require.New(s.t)
	require.Equal(s.filesReq, req)

	for _, f := range s.files {
		if err := srv.Send(f); err != nil {
			return err
		}
	}

	return nil
}
