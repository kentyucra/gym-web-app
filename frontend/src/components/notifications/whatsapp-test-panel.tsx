"use client";

import { useMutation } from "@tanstack/react-query";
import { AlertCircle, CheckCircle2, MessageCircle, Send } from "lucide-react";
import { FormEvent, useState } from "react";

import { sendWhatsAppTest, SendWhatsAppTestResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";

type FormState = {
  phone: string;
  text: string;
};

const initialForm: FormState = {
  phone: "",
  text: "Hello from Site Fitness",
};

export function WhatsAppTestPanel() {
  const [form, setForm] = useState<FormState>(initialForm);
  const [lastResult, setLastResult] = useState<SendWhatsAppTestResponse | null>(
    null,
  );

  const sendMutation = useMutation({
    mutationFn: () =>
      sendWhatsAppTest({
        phone: form.phone,
        text: form.text,
      }),
    onSuccess: (data) => {
      setLastResult(data);
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLastResult(null);
    sendMutation.mutate();
  }

  const delivery = lastResult?.delivery;

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,420px)_1fr]">
      <section className="rounded-lg border bg-card p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5" />
          <h2 className="text-xl font-semibold">WhatsApp test</h2>
        </div>

        <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
          <label className="block space-y-2">
            <span className="text-sm font-medium">Phone</span>
            <input
              className="h-10 w-full rounded-md border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
              value={form.phone}
              onChange={(event) =>
                setForm((current) => ({ ...current, phone: event.target.value }))
              }
              placeholder="948327856"
              required
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-medium">Message</span>
            <textarea
              className="min-h-28 w-full rounded-md border bg-background px-3 py-2 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20"
              value={form.text}
              onChange={(event) =>
                setForm((current) => ({ ...current, text: event.target.value }))
              }
              required
            />
          </label>

          {sendMutation.error ? (
            <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {sendMutation.error.message}
            </p>
          ) : null}

          <Button
            className="w-full"
            disabled={sendMutation.isPending}
            type="submit"
          >
            <Send />
            {sendMutation.isPending ? "Sending" : "Send test message"}
          </Button>
        </form>
      </section>

      <section className="rounded-lg border bg-card p-5 shadow-sm">
        <h2 className="text-xl font-semibold">Delivery result</h2>

        {delivery ? (
          <div className="mt-5 flex items-start gap-3 rounded-md border bg-muted/40 p-4">
            {delivery.sent ? (
              <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" />
            ) : (
              <AlertCircle className="mt-0.5 h-5 w-5 text-amber-700" />
            )}
            <div>
              <p className="font-medium">
                {delivery.sent ? "Message sent" : "Message not sent"}
              </p>
              <p className="mt-1 text-sm text-muted-foreground">
                {delivery.sent
                  ? `Delivered to ${delivery.chatId}.`
                  : delivery.reason ||
                    delivery.error ||
                    "OpenWA did not confirm delivery."}
              </p>
            </div>
          </div>
        ) : (
          <p className="mt-5 text-sm text-muted-foreground">
            Send a message to see the OpenWA delivery response.
          </p>
        )}
      </section>
    </div>
  );
}
