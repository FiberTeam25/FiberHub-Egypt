"use client";

import { useState } from "react";
import { useThreads, useThread, useSendMessage, useCreateThread, useMarkRead } from "@/hooks/useMessages";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { MessageSquare, Send, Plus, Loader2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

export default function MessagesPage() {
  const { user } = useAuthStore();
  const { data: threadData, isLoading } = useThreads();
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null);
  const { data: threadDetail } = useThread(selectedThreadId || "");
  const sendMessage = useSendMessage();
  const markRead = useMarkRead();
  const createThread = useCreateThread();
  const [newMsg, setNewMsg] = useState("");
  const [newThreadOpen, setNewThreadOpen] = useState(false);
  const [newThread, setNewThread] = useState({ participant_user_ids: "", subject: "", initial_message: "" });

  const threads = Array.isArray(threadData) ? threadData : threadData?.items || [];

  const handleSend = () => {
    if (!newMsg.trim() || !selectedThreadId) return;
    sendMessage.mutate({ threadId: selectedThreadId, content: newMsg });
    setNewMsg("");
  };

  const handleSelectThread = (id: string) => {
    setSelectedThreadId(id);
    markRead.mutate(id);
  };

  const handleCreateThread = () => {
    const ids = newThread.participant_user_ids.split(",").map(s => s.trim()).filter(Boolean);
    if (!ids.length || !newThread.initial_message) return;
    createThread.mutate({
      context_type: "direct",
      subject: newThread.subject || undefined,
      participant_user_ids: ids,
      initial_message: newThread.initial_message,
    }, {
      onSuccess: () => {
        setNewThreadOpen(false);
        setNewThread({ participant_user_ids: "", subject: "", initial_message: "" });
      },
    });
  };

  const messages = threadDetail?.messages || [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Messages</h1>
        <Dialog open={newThreadOpen} onOpenChange={setNewThreadOpen}>
          <DialogTrigger render={<Button size="sm" />}>
            <Plus className="h-4 w-4 mr-2" />New Conversation
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>New Conversation</DialogTitle></DialogHeader>
            <div className="space-y-4">
              <div><label className="text-sm font-medium">Participant User IDs (comma-separated)</label><Input value={newThread.participant_user_ids} onChange={(e) => setNewThread({ ...newThread, participant_user_ids: e.target.value })} placeholder="user-id-1, user-id-2" /></div>
              <div><label className="text-sm font-medium">Subject</label><Input value={newThread.subject} onChange={(e) => setNewThread({ ...newThread, subject: e.target.value })} /></div>
              <div><label className="text-sm font-medium">Message</label><Textarea value={newThread.initial_message} onChange={(e) => setNewThread({ ...newThread, initial_message: e.target.value })} /></div>
              <Button onClick={handleCreateThread} disabled={createThread.isPending}>{createThread.isPending ? "Creating..." : "Create"}</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-[calc(100vh-12rem)]">
        {/* Thread list */}
        <div className="border rounded-lg overflow-y-auto">
          {isLoading ? (
            <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin" /></div>
          ) : threads.length === 0 ? (
            <div className="text-center py-8 text-sm text-muted-foreground">No conversations yet</div>
          ) : (
            threads.map((t: { id: string; subject?: string; unread_count?: number; last_message?: string; updated_at?: string; created_at: string }) => (
              <div
                key={t.id}
                className={`p-3 border-b cursor-pointer hover:bg-muted/50 transition-colors ${selectedThreadId === t.id ? "bg-muted" : ""}`}
                onClick={() => handleSelectThread(t.id)}
              >
                <div className="flex items-center justify-between">
                  <p className="font-medium text-sm truncate">{t.subject || "Direct message"}</p>
                  {(t.unread_count ?? 0) > 0 && <Badge variant="destructive" className="text-xs">{t.unread_count}</Badge>}
                </div>
                <p className="text-xs text-muted-foreground truncate mt-1">{t.last_message || "No messages"}</p>
                <p className="text-xs text-muted-foreground mt-1">{formatDistanceToNow(new Date(t.updated_at || t.created_at), { addSuffix: true })}</p>
              </div>
            ))
          )}
        </div>

        {/* Conversation */}
        <div className="lg:col-span-2 border rounded-lg flex flex-col">
          {selectedThreadId ? (
            <>
              <div className="p-3 border-b">
                <p className="font-medium text-sm">{threadDetail?.subject || "Conversation"}</p>
                <p className="text-xs text-muted-foreground capitalize">{threadDetail?.context_type} thread</p>
              </div>
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.map((m: { id: string; sender_id: string; sender_name?: string; content: string; created_at: string }) => {
                  const isMine = m.sender_id === user?.id;
                  return (
                    <div key={m.id} className={`flex ${isMine ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[70%] rounded-lg px-3 py-2 text-sm ${isMine ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                        {!isMine && <p className="text-xs font-medium mb-1">{m.sender_name || "User"}</p>}
                        <p>{m.content}</p>
                        <p className="text-xs opacity-70 mt-1">{new Date(m.created_at).toLocaleTimeString()}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="p-3 border-t flex gap-2">
                <Input
                  value={newMsg}
                  onChange={(e) => setNewMsg(e.target.value)}
                  placeholder="Type a message..."
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                />
                <Button size="icon" onClick={handleSend} disabled={sendMessage.isPending}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <MessageSquare className="h-8 w-8 mx-auto mb-2" />
                <p className="text-sm">Select a conversation</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
