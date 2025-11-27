import Image from "next/image";
import { useEffect, useState } from "react";

import { useFromConnectionsContext } from "@/app/chat/[chatId]/components/ActionsBar/components/KnowledgeToFeed/components/FromConnections/FromConnectionsProvider/hooks/useFromConnectionContext";
import { OpenedConnection, Provider, Sync } from "@/lib/api/sync/types";
import { useSync } from "@/lib/api/sync/useSync";
import { QuivrButton } from "@/lib/components/ui/QuivrButton/QuivrButton";
import { iconList } from "@/lib/helpers/iconList";

import { ConnectionButton } from "./ConnectionButton/ConnectionButton";
import { ConnectionLine } from "./ConnectionLine/ConnectionLine";
import styles from "./ConnectionSection.module.scss";

import { ConnectionIcon } from "../../ui/ConnectionIcon/ConnectionIcon";
import { Icon } from "../../ui/Icon/Icon";
import { TextButton } from "../../ui/TextButton/TextButton";
import Tooltip from "../../ui/Tooltip/Tooltip";

interface ConnectionSectionProps {
  label: string;
  provider: Provider;
  callback: (name: string) => Promise<{ authorization_url: string }>;
  fromAddKnowledge?: boolean;
  oneAccountLimitation?: boolean;
}

export const ConnectionSection = ({
  label,
  provider,
  fromAddKnowledge,
  callback,
  oneAccountLimitation,
}: ConnectionSectionProps): JSX.Element => {
  const { providerIconUrls, getUserSyncs, getSyncFiles } = useSync();
  const {
    setCurrentSyncElements,
    setCurrentSyncId,
    setOpenedConnections,
    openedConnections,
    hasToReload,
    setHasToReload,
    setLoadingFirstList,
    setCurrentProvider,
  } = useFromConnectionsContext();
  const [existingConnections, setExistingConnections] = useState<Sync[]>([]);
  const [folded, setFolded] = useState<boolean>(!fromAddKnowledge);

  const fetchUserSyncs = async () => {
    try {
      const res: Sync[] = await getUserSyncs();
      setExistingConnections(
        res.filter(
          (sync) =>
            Object.keys(sync.credentials).length !== 0 &&
            sync.provider === provider
        )
      );
    } catch (error) {
      console.error(error);
    }
  };

  const getButtonIcon = (): keyof typeof iconList => {
    return existingConnections.filter(
      (connection) => connection.status !== "REMOVED"
    ).length > 0
      ? "add"
      : "sync";
  };

  const getButtonName = (): string => {
    return existingConnections.filter(
      (connection) => connection.status !== "REMOVED"
    ).length > 0
      ? "Add more"
      : "Connect";
  };

  useEffect(() => {
    void fetchUserSyncs();
  }, []);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible" && !document.hidden) {
        void fetchUserSyncs();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  useEffect(() => {
    if (hasToReload) {
      void fetchUserSyncs();
      setHasToReload(false);
    }
  }, [hasToReload]);

  const handleOpenedConnections = (userSyncId: number) => {
    const existingConnection = openedConnections.find(
      (connection) => connection.user_sync_id === userSyncId
    );

    if (!existingConnection) {
      const newConnection: OpenedConnection = {
        name:
          existingConnections.find((connection) => connection.id === userSyncId)
            ?.name ?? "",
        user_sync_id: userSyncId,
        id: undefined,
        provider: provider,
        submitted: false,
        selectedFiles: { files: [] },
        last_synced: "",
      };

      setOpenedConnections([...openedConnections, newConnection]);
    }
  };

  const handleGetSyncFiles = async (userSyncId: number, syncProvider: Provider) => {
    try {
      setLoadingFirstList(true);
      const res = await getSyncFiles(userSyncId, undefined, syncProvider);
      setLoadingFirstList(false);
      setCurrentSyncElements(res);
      setCurrentSyncId(userSyncId);
      handleOpenedConnections(userSyncId);
    } catch (error) {
      console.error("Failed to get sync files:", error);
      setLoadingFirstList(false);
    }
  };

  const connect = async () => {
    // Generate a better default connection name
    const timestamp = new Date().toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    const defaultName = provider === "Moodle"
      ? `Moodle Verbindung ${timestamp}`
      : `${provider} Connection ${timestamp}`;

    const res = await callback(defaultName);
    if (res.authorization_url) {
      // Set up message listener for auth token requests from popup
      const messageHandler = (event: MessageEvent) => {
        console.log('[Parent] Received message:', event.origin, event.data);

        // Only accept messages from localhost
        if (!event.origin.startsWith('http://localhost:')) {
          console.log('[Parent] Rejected non-localhost message');
          return;
        }

        if (event.data.type === 'AUTH_TOKEN_REQUEST') {
          console.log('[Parent] Received AUTH_TOKEN_REQUEST, getting token');

          let token = '';

          try {
            // Try localStorage first
            const supabaseSession = localStorage.getItem('supabase-auth-token');
            console.log('[Parent] localStorage key exists:', !!supabaseSession);

            if (supabaseSession) {
              const session = JSON.parse(supabaseSession);
              token = session?.access_token || '';
            }

            // If not in localStorage, try cookies
            if (!token) {
              console.log('[Parent] Trying to get token from cookies');
              const cookieValue = document.cookie
                .split('; ')
                .find(row => row.startsWith('supabase-auth-token='));

              if (cookieValue) {
                const encodedValue = cookieValue.split('=')[1];
                const decodedValue = decodeURIComponent(encodedValue);
                console.log('[Parent] Found cookie, decoded value:', decodedValue.substring(0, 50));

                // Cookie format: ["access_token", "refresh_token", null, null, null]
                const tokenArray = JSON.parse(decodedValue);
                token = tokenArray[0] || '';
              }
            }

            console.log('[Parent] Sending token back to popup, token length:', token.length);

            // Send token back to popup
            event.source?.postMessage(
              { type: 'AUTH_TOKEN_RESPONSE', token },
              event.origin as any
            );
          } catch (e) {
            console.error('[Parent] Error getting auth token:', e);
            // Send empty token on error
            event.source?.postMessage(
              { type: 'AUTH_TOKEN_RESPONSE', token: '' },
              event.origin as any
            );
          }
        }
      };

      window.addEventListener('message', messageHandler);

      // Open as a centered popup window
      const width = 600;
      const height = 700;
      const left = (window.screen.width - width) / 2;
      const top = (window.screen.height - height) / 2;
      const features = `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`;
      const popup = window.open(res.authorization_url, "moodle-connect", features);

      // Clean up listener when popup closes
      const checkPopupClosed = setInterval(() => {
        if (popup?.closed) {
          window.removeEventListener('message', messageHandler);
          clearInterval(checkPopupClosed);
        }
      }, 1000);
    }
  };

  const renderConnectionLines = (
    connections: Sync[],
    connectionFolded: boolean
  ) => {
    if (!connectionFolded) {
      return connections
        .filter((connection) => connection.status !== "REMOVED")
        .map((connection, index) => (
          <ConnectionLine
            key={index}
            label={provider === "Moodle" ? connection.name : connection.email}
            index={index}
            id={connection.id}
            warnUserOnDelete={provider === "Notion"}
          />
        ));
    } else {
      return (
        <div className={styles.folded}>
          {connections.map((connection, index) => {
            const displayLabel = provider === "Moodle" ? connection.name : connection.email;
            return (
              <ConnectionIcon
                key={index}
                letter={displayLabel[0] || "?"}
                index={index}
              />
            );
          })}
        </div>
      );
    }
  };

  const renderExistingConnections = () => {
    const activeConnections = existingConnections.filter(
      (connection) => connection.status !== "REMOVED"
    );

    if (activeConnections.length === 0) {
      return null;
    }

    if (!fromAddKnowledge) {
      return (
        <div className={styles.existing_connections}>
          <div className={styles.existing_connections_header}>
            <span className={styles.label}>Connected accounts</span>
            <Icon
              name="settings"
              size="normal"
              color="black"
              handleHover={true}
              onClick={() => setFolded(!folded)}
            />
          </div>
          {renderConnectionLines(activeConnections, folded)}
        </div>
      );
    } else {
      return (
        <div className={styles.existing_connections}>
          {activeConnections.map((connection, index) => (
            <ConnectionButton
              key={index}
              label={connection.provider === "Moodle" ? connection.name : connection.email}
              index={index}
              submitted={openedConnections.some(
                (openedConnection) =>
                  openedConnection.name === connection.name &&
                  openedConnection.submitted
              )}
              onClick={() => {
                setCurrentProvider(connection.provider);
                void handleGetSyncFiles(connection.id, connection.provider);
              }}
              sync={connection}
            />
          ))}
        </div>
      );
    }
  };

  return (
    <>
      <div className={styles.connection_section_wrapper}>
        <div className={styles.connection_section_header}>
          <div className={styles.left}>
            <Image
              src={providerIconUrls[provider]}
              alt={label}
              width={24}
              height={24}
            />
            <span className={styles.label}>{label}</span>
          </div>
          {!fromAddKnowledge &&
          (!oneAccountLimitation || existingConnections.length === 0) ? (
            <QuivrButton
              iconName={getButtonIcon()}
              label={getButtonName()}
              color="primary"
              onClick={connect}
              small={true}
            />
          ) : existingConnections[0] &&
            existingConnections[0].status === "REMOVED" ? (
            <Tooltip tooltip={`We are deleting your connection.`}>
              <div className={styles.deleting_wrapper}>
                <Icon name="waiting" size="small" color="warning" />
                <span className={styles.deleting_mention}>Deleting</span>
              </div>
            </Tooltip>
          ) : null}

          {fromAddKnowledge &&
            (!oneAccountLimitation || existingConnections.length === 0) && (
              <TextButton
                iconName={getButtonIcon()}
                label={getButtonName()}
                color="black"
                onClick={connect}
                small={true}
              />
            )}
        </div>
        {renderExistingConnections()}
      </div>
    </>
  );
};
