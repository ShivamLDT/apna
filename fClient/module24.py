     # def process_files(self, f_files, key, job_id, OpendedSh=None, **kwargs):
     #    iNotDone = 0
     #    total_files = len(f_files)
     #    futures = []

     #    try:
     #        # Wait for scheduler to be ready
     #        wait_for_job_ready(job_id, self.app)

     #        for i, file in enumerate(f_files, 1):
     #            # Clone and adjust kwargs for each file
     #            job_kwargs = kwargs.copy()
     #            job_kwargs["kwargs"] = dict(kwargs.get("kwargs", {}))  # deep copy
     #            job_kwargs["kwargs"]["total_chunks"] = "1"
     #            job_kwargs["kwargs"]["totalfiles"] = str(total_files)
     #            job_kwargs["kwargs"]["currentfile"] = str(i)
     #            job_kwargs["kwargs"]["iNotDone"] = str(iNotDone)

     #            def worker(file_path=file, idx=i, job_kwargs=job_kwargs):
     #                try:
     #                    self.save_file(file_path, key, job_id, OpendedSh=OpendedSh, **job_kwargs)
     #                    job_kwargs["kwargs"]["filesdone"] = str(idx - iNotDone)
     #                    # self.dispatcher.send(signal=self.UPLOADED_JOB, sender=self, job_id=job_id, kwargs=job_kwargs)
     #                except Exception as ex:
     #                    nonlocal iNotDone
     #                    iNotDone += 1
     #                    self.dispatcher.send(signal=self.ERROR, sender=self, __doc__=ex.__doc__)
     #                    print(f"[ERROR] {str(ex)}")
     #                    traceback.print_exc()

     #            futures.append(self.executor.submit(worker))

     #        for future in as_completed(futures):
     #            # Result fetch to surface exceptions, if any
     #            try:
     #                future.result()
     #            except Exception as ex:
     #                self.dispatcher.send(signal=self.ERROR, sender=self, __doc__=ex.__doc__)
     #                print(f"[FUTURE ERROR] {str(ex)}")
     #                traceback.print_exc()

     #    except Exception as ex:
     #        self.dispatcher.send(signal=self.ERROR, sender=self, __doc__=ex.__doc__)
     #        print(f"[MAIN ERROR] {str(ex)}")
     #        traceback.print_exc()
