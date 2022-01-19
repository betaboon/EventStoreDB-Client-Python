# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: gossip.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import Dict, List

import betterproto
from betterproto.grpc.grpclib_server import ServiceBase
import grpclib


class MemberInfoVNodeState(betterproto.Enum):
    Initializing = 0
    DiscoverLeader = 1
    Unknown = 2
    PreReplica = 3
    CatchingUp = 4
    Clone = 5
    Follower = 6
    PreLeader = 7
    Leader = 8
    Manager = 9
    ShuttingDown = 10
    Shutdown = 11
    ReadOnlyLeaderless = 12
    PreReadOnlyReplica = 13
    ReadOnlyReplica = 14
    ResigningLeader = 15


@dataclass(eq=False, repr=False)
class ClusterInfo(betterproto.Message):
    members: List["MemberInfo"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class EndPoint(betterproto.Message):
    address: str = betterproto.string_field(1)
    port: int = betterproto.uint32_field(2)


@dataclass(eq=False, repr=False)
class MemberInfo(betterproto.Message):
    instance_id: "__client__.Uuid" = betterproto.message_field(1)
    time_stamp: int = betterproto.int64_field(2)
    state: "MemberInfoVNodeState" = betterproto.enum_field(3)
    is_alive: bool = betterproto.bool_field(4)
    http_end_point: "EndPoint" = betterproto.message_field(5)


class GossipStub(betterproto.ServiceStub):
    async def read(self) -> "ClusterInfo":

        request = __client__.Empty()

        return await self._unary_unary(
            "/event_store.client.gossip.Gossip/Read", request, ClusterInfo
        )


class GossipBase(ServiceBase):
    async def read(self) -> "ClusterInfo":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_read(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {}

        response = await self.read(**request_kwargs)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/event_store.client.gossip.Gossip/Read": grpclib.const.Handler(
                self.__rpc_read,
                grpclib.const.Cardinality.UNARY_UNARY,
                __client__.Empty,
                ClusterInfo,
            ),
        }


from ... import client as __client__
